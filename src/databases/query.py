"""
Query Orchestration Module

This module provides functionality for orchestrating queries across different database systems.
It handles routing queries to the appropriate database, combining results, and caching.
"""

import logging
import time
import json
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .base import BaseDBConnector
from .relational import PostgreSQLConnector
from .document import MongoDBConnector
from .graph import Neo4jConnector
from .vector import PineconeConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryOrchestrator:
    """
    Query orchestrator for routing queries across different database systems.
    
    This class provides methods to route queries to the appropriate database,
    combine results, and cache frequently accessed data.
    """
    
    def __init__(self, connectors: Dict[str, BaseDBConnector], config: Dict[str, Any] = None):
        """
        Initialize the query orchestrator with database connectors.
        
        Args:
            connectors: Dictionary of database connectors with keys 'relational', 'document',
                       'graph', and 'vector'.
            config: Optional configuration parameters for query orchestration.
        """
        self.connectors = connectors
        self.config = config or {}
        
        # Extract connectors
        self.relational_db = connectors.get('relational')
        self.document_db = connectors.get('document')
        self.graph_db = connectors.get('graph')
        self.vector_db = connectors.get('vector')
        
        # Query orchestration settings
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl = self.config.get('cache_ttl', 300)  # seconds
        self.cache_size = self.config.get('cache_size', 1000)  # number of items
        self.query_timeout = self.config.get('query_timeout', 30)  # seconds
        
        # Initialize cache
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Query templates
        self.query_templates = {
            'member_details': {
                'description': 'Get detailed information about a member',
                'databases': ['relational', 'document', 'graph'],
                'parameters': ['member_id'],
                'queries': {
                    'relational': "SELECT * FROM {schema}.members WHERE id = '{member_id}'",
                    'document': {'member_id': '{member_id}'},
                    'graph': "MATCH (m:Member {id: '{member_id}'}) RETURN m"
                },
                'collections': {
                    'document': 'clinical_notes'
                },
                'result_processing': 'combine_member_details'
            },
            'member_conditions': {
                'description': 'Get conditions for a member',
                'databases': ['relational', 'graph'],
                'parameters': ['member_id'],
                'queries': {
                    'relational': "SELECT * FROM {schema}.conditions WHERE member_id = '{member_id}'",
                    'graph': """
                    MATCH (m:Member {id: '{member_id}'})-[:HAS_CONDITION]->(c:Condition)
                    RETURN c
                    """
                },
                'result_processing': 'combine_member_conditions'
            },
            'member_medications': {
                'description': 'Get medications for a member',
                'databases': ['relational', 'graph'],
                'parameters': ['member_id'],
                'queries': {
                    'relational': "SELECT * FROM {schema}.medications WHERE member_id = '{member_id}'",
                    'graph': """
                    MATCH (m:Member {id: '{member_id}'})-[:TAKES_MEDICATION]->(med:Medication)
                    RETURN med
                    """
                },
                'result_processing': 'combine_member_medications'
            },
            'member_encounters': {
                'description': 'Get encounters for a member',
                'databases': ['relational', 'graph'],
                'parameters': ['member_id'],
                'queries': {
                    'relational': "SELECT * FROM {schema}.encounters WHERE member_id = '{member_id}'",
                    'graph': """
                    MATCH (m:Member {id: '{member_id}'})-[:HAD_ENCOUNTER]->(e:Encounter)
                    RETURN e
                    """
                },
                'result_processing': 'combine_member_encounters'
            },
            'member_claims': {
                'description': 'Get claims for a member',
                'databases': ['relational', 'graph'],
                'parameters': ['member_id'],
                'queries': {
                    'relational': "SELECT * FROM {schema}.claims WHERE member_id = '{member_id}'",
                    'graph': """
                    MATCH (m:Member {id: '{member_id}'})-[:HAD_ENCOUNTER]->()-[:GENERATED]->(c:Claim)
                    RETURN c
                    """
                },
                'result_processing': 'combine_member_claims'
            },
            'member_authorizations': {
                'description': 'Get authorizations for a member',
                'databases': ['relational', 'document', 'graph'],
                'parameters': ['member_id'],
                'queries': {
                    'relational': "SELECT * FROM {schema}.authorizations WHERE member_id = '{member_id}'",
                    'document': {'member_id': '{member_id}'},
                    'graph': """
                    MATCH (m:Member {id: '{member_id}'})-[:REQUESTED]->(a:Authorization)
                    RETURN a
                    """
                },
                'collections': {
                    'document': 'authorization_rationales'
                },
                'result_processing': 'combine_member_authorizations'
            },
            'member_clinical_notes': {
                'description': 'Get clinical notes for a member',
                'databases': ['document', 'vector'],
                'parameters': ['member_id'],
                'queries': {
                    'document': {'member_id': '{member_id}'},
                    'vector': {
                        'filter': {'member_id': '{member_id}'},
                        'top_k': 100
                    }
                },
                'collections': {
                    'document': 'clinical_notes',
                    'vector': 'clinical_notes'
                },
                'result_processing': 'combine_member_clinical_notes'
            },
            'semantic_search': {
                'description': 'Perform semantic search across all text content',
                'databases': ['vector'],
                'parameters': ['query_text', 'top_k'],
                'queries': {
                    'vector': {
                        'vector': '{query_embedding}',
                        'top_k': '{top_k}'
                    }
                },
                'collections': {
                    'vector': None  # Search across all collections
                },
                'result_processing': 'process_semantic_search'
            },
            'provider_network': {
                'description': 'Get provider network information',
                'databases': ['graph'],
                'parameters': ['provider_id'],
                'queries': {
                    'graph': """
                    MATCH (p:Provider {id: '{provider_id}'})-[r]-(other)
                    RETURN p, r, other
                    """
                },
                'result_processing': 'process_provider_network'
            },
            'care_episode_details': {
                'description': 'Get details for a care episode',
                'databases': ['graph', 'document'],
                'parameters': ['episode_id'],
                'queries': {
                    'graph': """
                    MATCH (e:CareEpisode {id: '{episode_id}'})-[r]-(other)
                    RETURN e, r, other
                    """,
                    'document': {'care_episode_id': '{episode_id}'}
                },
                'collections': {
                    'document': 'clinical_notes'
                },
                'result_processing': 'combine_care_episode_details'
            }
        }
    
    def execute_query(self, query_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a query using the specified template and parameters.
        
        Args:
            query_name: Name of the query template to use.
            parameters: Parameters to substitute in the query template.
            
        Returns:
            Dictionary containing the query results.
        """
        # Check if query template exists
        if query_name not in self.query_templates:
            logger.error(f"Query template '{query_name}' not found")
            return {'error': f"Query template '{query_name}' not found"}
        
        # Check cache if enabled
        if self.cache_enabled:
            cache_key = self._generate_cache_key(query_name, parameters)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
        
        # Get query template
        template = self.query_templates[query_name]
        
        # Execute queries on each database
        results = {}
        for db_type in template['databases']:
            db_connector = self.connectors.get(db_type)
            if not db_connector or not db_connector.is_connected:
                logger.warning(f"Database connector '{db_type}' not available for query '{query_name}'")
                continue
            
            # Get query for this database
            db_query = template['queries'].get(db_type)
            if not db_query:
                logger.warning(f"No query defined for database '{db_type}' in template '{query_name}'")
                continue
            
            # Substitute parameters in query
            if isinstance(db_query, str):
                # For SQL or Cypher queries
                for param_name, param_value in parameters.items():
                    db_query = db_query.replace(f"{{{param_name}}}", str(param_value))
                
                # Special handling for relational database schema
                if db_type == 'relational' and '{schema}' in db_query:
                    db_query = db_query.replace('{schema}', self.relational_db.schema)
            elif isinstance(db_query, dict):
                # For document or vector queries
                processed_query = {}
                for key, value in db_query.items():
                    if isinstance(value, str) and '{' in value and '}' in value:
                        # Parameter substitution in string values
                        for param_name, param_value in parameters.items():
                            if f"{{{param_name}}}" in value:
                                value = value.replace(f"{{{param_name}}}", str(param_value))
                        processed_query[key] = value
                    else:
                        processed_query[key] = value
                
                db_query = processed_query
                
                # Special handling for vector database query embedding
                if db_type == 'vector' and 'vector' in db_query and db_query['vector'] == '{query_embedding}':
                    # Generate embedding for query text
                    from .sync import DatabaseSynchronizer
                    query_text = parameters.get('query_text', '')
                    db_query['vector'] = DatabaseSynchronizer._generate_embedding(None, query_text)
            
            # Get collection name if applicable
            collection_name = None
            if 'collections' in template and db_type in template['collections']:
                collection_name = template['collections'][db_type]
                
                # Substitute parameters in collection name if it's a string
                if isinstance(collection_name, str) and '{' in collection_name and '}' in collection_name:
                    for param_name, param_value in parameters.items():
                        collection_name = collection_name.replace(f"{{{param_name}}}", str(param_value))
            
            # Execute query
            try:
                start_time = time.time()
                db_result = db_connector.query(db_query, collection_name)
                end_time = time.time()
                
                results[db_type] = {
                    'data': db_result,
                    'query_time': end_time - start_time,
                    'record_count': len(db_result) if isinstance(db_result, list) else 1
                }
                
                logger.info(f"Query '{query_name}' on '{db_type}' returned {results[db_type]['record_count']} records in {results[db_type]['query_time']:.3f} seconds")
            except Exception as e:
                logger.error(f"Error executing query '{query_name}' on '{db_type}': {e}")
                results[db_type] = {'error': str(e)}
        
        # Process results
        if 'result_processing' in template:
            processor_name = template['result_processing']
            if hasattr(self, processor_name):
                processor = getattr(self, processor_name)
                processed_result = processor(results, parameters)
            else:
                logger.warning(f"Result processor '{processor_name}' not found")
                processed_result = {'results': results, 'parameters': parameters}
        else:
            processed_result = {'results': results, 'parameters': parameters}
        
        # Cache result if enabled
        if self.cache_enabled:
            self._add_to_cache(cache_key, processed_result)
        
        return processed_result
    
    def execute_custom_query(self, db_type: str, query: Any, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a custom query on a specific database.
        
        Args:
            db_type: Type of database to query ('relational', 'document', 'graph', 'vector').
            query: Query to execute (format depends on the database type).
            collection_name: Optional name of the collection/table to query.
            
        Returns:
            Dictionary containing the query results.
        """
        # Get database connector
        db_connector = self.connectors.get(db_type)
        if not db_connector or not db_connector.is_connected:
            logger.error(f"Database connector '{db_type}' not available")
            return {'error': f"Database connector '{db_type}' not available"}
        
        # Execute query
        try:
            start_time = time.time()
            result = db_connector.query(query, collection_name)
            end_time = time.time()
            
            return {
                'data': result,
                'query_time': end_time - start_time,
                'record_count': len(result) if isinstance(result, list) else 1
            }
        except Exception as e:
            logger.error(f"Error executing custom query on '{db_type}': {e}")
            return {'error': str(e)}
    
    def _generate_cache_key(self, query_name: str, parameters: Dict[str, Any]) -> str:
        """Generate a cache key for a query."""
        # Sort parameters to ensure consistent key generation
        sorted_params = sorted(parameters.items())
        param_str = json.dumps(sorted_params)
        return f"{query_name}:{param_str}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get a result from the cache if it exists and is not expired."""
        if cache_key in self.cache:
            # Check if cache entry is expired
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp <= self.cache_ttl:
                self.cache_hits += 1
                return self.cache[cache_key]
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
        
        self.cache_misses += 1
        return None
    
    def _add_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Add a result to the cache."""
        # Enforce cache size limit
        if len(self.cache) >= self.cache_size:
            # Remove oldest cache entry
            oldest_key = min(self.cache_timestamps, key=self.cache_timestamps.get)
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]
        
        # Add to cache
        self.cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()
    
    def clear_cache(self) -> None:
        """Clear the query cache."""
        self.cache = {}
        self.cache_timestamps = {}
        logger.info("Query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the query cache."""
        return {
            'cache_enabled': self.cache_enabled,
            'cache_size': len(self.cache),
            'cache_max_size': self.cache_size,
            'cache_ttl': self.cache_ttl,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_ratio': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }
    
    # Result processors
    
    def combine_member_details(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine member details from multiple databases."""
        combined_result = {'member_id': parameters.get('member_id')}
        
        # Add basic member information from relational database
        if 'relational' in results and 'data' in results['relational'] and results['relational']['data']:
            member_data = results['relational']['data'][0] if isinstance(results['relational']['data'], list) else results['relational']['data']
            combined_result.update(member_data)
        
        # Add clinical notes from document database
        if 'document' in results and 'data' in results['document']:
            combined_result['clinical_notes'] = results['document']['data']
        
        # Add graph relationships
        if 'graph' in results and 'data' in results['graph']:
            combined_result['relationships'] = results['graph']['data']
        
        return combined_result
    
    def combine_member_conditions(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine member conditions from multiple databases."""
        combined_result = {'member_id': parameters.get('member_id'), 'conditions': []}
        
        # Add conditions from relational database
        if 'relational' in results and 'data' in results['relational']:
            combined_result['conditions'].extend(results['relational']['data'])
        
        # Add conditions from graph database
        if 'graph' in results and 'data' in results['graph']:
            for node in results['graph']['data']:
                if 'c' in node:  # 'c' is the alias for Condition in the Cypher query
                    combined_result['conditions'].append(node['c'])
        
        return combined_result
    
    def combine_member_medications(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine member medications from multiple databases."""
        combined_result = {'member_id': parameters.get('member_id'), 'medications': []}
        
        # Add medications from relational database
        if 'relational' in results and 'data' in results['relational']:
            combined_result['medications'].extend(results['relational']['data'])
        
        # Add medications from graph database
        if 'graph' in results and 'data' in results['graph']:
            for node in results['graph']['data']:
                if 'med' in node:  # 'med' is the alias for Medication in the Cypher query
                    combined_result['medications'].append(node['med'])
        
        return combined_result
    
    def combine_member_encounters(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine member encounters from multiple databases."""
        combined_result = {'member_id': parameters.get('member_id'), 'encounters': []}
        
        # Add encounters from relational database
        if 'relational' in results and 'data' in results['relational']:
            combined_result['encounters'].extend(results['relational']['data'])
        
        # Add encounters from graph database
        if 'graph' in results and 'data' in results['graph']:
            for node in results['graph']['data']:
                if 'e' in node:  # 'e' is the alias for Encounter in the Cypher query
                    combined_result['encounters'].append(node['e'])
        
        return combined_result
    
    def combine_member_claims(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine member claims from multiple databases."""
        combined_result = {'member_id': parameters.get('member_id'), 'claims': []}
        
        # Add claims from relational database
        if 'relational' in results and 'data' in results['relational']:
            combined_result['claims'].extend(results['relational']['data'])
        
        # Add claims from graph database
        if 'graph' in results and 'data' in results['graph']:
            for node in results['graph']['data']:
                if 'c' in node:  # 'c' is the alias for Claim in the Cypher query
                    combined_result['claims'].append(node['c'])
        
        return combined_result
    
    def combine_member_authorizations(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine member authorizations from multiple databases."""
        combined_result = {'member_id': parameters.get('member_id'), 'authorizations': []}
        
        # Add authorizations from relational database
        if 'relational' in results and 'data' in results['relational']:
            combined_result['authorizations'].extend(results['relational']['data'])
        
        # Add authorization rationales from document database
        if 'document' in results and 'data' in results['document']:
            combined_result['authorization_rationales'] = results['document']['data']
        
        # Add authorizations from graph database
        if 'graph' in results and 'data' in results['graph']:
            for node in results['graph']['data']:
                if 'a' in node:  # 'a' is the alias for Authorization in the Cypher query
                    combined_result['authorizations'].append(node['a'])
        
        return combined_result
    
    def combine_member_clinical_notes(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine member clinical notes from multiple databases."""
        combined_result = {'member_id': parameters.get('member_id'), 'clinical_notes': []}
        
        # Add clinical notes from document database
        if 'document' in results and 'data' in results['document']:
            combined_result['clinical_notes'].extend(results['document']['data'])
        
        # Add clinical notes from vector database
        if 'vector' in results and 'data' in results['vector']:
            # Extract clinical notes from vector search results
            for item in results['vector']['data']:
                if 'metadata' in item and 'entity_type' in item['metadata'] and item['metadata']['entity_type'] == 'clinical_notes':
                    # Get the full clinical note from the document database
                    note_id = item['id']
                    for note in combined_result['clinical_notes']:
                        if note['id'] == note_id or note.get('_id') == note_id:
                            # Add vector similarity score to the note
                            note['similarity_score'] = item['score']
                            break
        
        return combined_result
    
    def process_semantic_search(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process semantic search results."""
        combined_result = {
            'query_text': parameters.get('query_text', ''),
            'results': []
        }
        
        # Add results from vector database
        if 'vector' in results and 'data' in results['vector']:
            for item in results['vector']['data']:
                result_item = {
                    'id': item['id'],
                    'score': item['score'],
                    'metadata': item.get('metadata', {})
                }
                combined_result['results'].append(result_item)
        
        return combined_result
    
    def process_provider_network(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process provider network results."""
        combined_result = {
            'provider_id': parameters.get('provider_id', ''),
            'network': []
        }
        
        # Add results from graph database
        if 'graph' in results and 'data' in results['graph']:
            for item in results['graph']['data']:
                if 'p' in item and 'r' in item and 'other' in item:
                    relationship = {
                        'provider': item['p'],
                        'relationship_type': type(item['r']).__name__,
                        'related_entity': item['other']
                    }
                    combined_result['network'].append(relationship)
        
        return combined_result
    
    def combine_care_episode_details(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Combine care episode details from multiple databases."""
        combined_result = {
            'episode_id': parameters.get('episode_id', ''),
            'details': {},
            'related_entities': [],
            'clinical_notes': []
        }
        
        # Add care episode details from graph database
        if 'graph' in results and 'data' in results['graph']:
            for item in results['graph']['data']:
                if 'e' in item:
                    # Add episode details if not already added
                    if not combined_result['details']:
                        combined_result['details'] = item['e']
                
                if 'r' in item and 'other' in item:
                    relationship = {
                        'relationship_type': type(item['r']).__name__,
                        'related_entity': item['other']
                    }
                    combined_result['related_entities'].append(relationship)
        
        # Add clinical notes from document database
        if 'document' in results and 'data' in results['document']:
            combined_result['clinical_notes'] = results['document']['data']
        
        return combined_result