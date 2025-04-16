# Memory Bank Organization Guide

This document provides an overview of the memory bank organization for the Synthetic Healthcare Data Generator project.

2025-03-19 11:42:00 - Created during memory bank reorganization.
2025-03-19 11:44:00 - Updated with final structure.

## Memory Bank Structure

The memory bank has been reorganized to improve clarity, reduce redundancy, and provide better organization of project information. The structure now consists of:

### Core Files
- **productContext.md** - High-level project overview and goals
- **activeContext.md** - Current focus, recent changes, and open questions
- **decisionLog.md** - Key architectural and implementation decisions
- **progress.md** - Task tracking (completed, current, and next steps)
- **systemPatterns.md** - Reusable patterns and standards for the project

### Consolidated Technical Documentation
- **architecture.md** - Comprehensive architecture documentation
- **data_model.md** - Complete data model documentation
- **implementation_strategy.md** - Implementation approach and plan
- **rag_strategy.md** - RAG testing and unstructured data approach

### README
- **README.md** (this file) - Guide to the memory bank organization

## File Descriptions

### Core Files

#### productContext.md
Contains the high-level overview of the project, including project goals, key features, and overall architecture. This is the starting point for understanding the project.

#### activeContext.md
Tracks the project's current status, including current focus areas, recent changes, and open questions/issues. This file is regularly updated as the project progresses.

#### decisionLog.md
Records key architectural and implementation decisions, including the rationale and implementation details for each decision.

#### progress.md
Tracks the project's progress using a task list format, organized into completed tasks, current tasks, and next steps.

#### systemPatterns.md
Documents recurring patterns and standards used in the project, including coding patterns, architectural patterns, and testing patterns.

### Consolidated Technical Documentation

#### architecture.md
Provides a comprehensive view of the solution architecture, including system components, data flows, database design, and implementation considerations. This file consolidates information previously spread across multiple files.

#### data_model.md
Documents the complete data model, including core entities, enhanced healthcare entities, relationships, and data consistency rules. This file merges information from multiple previous files.

#### implementation_strategy.md
Outlines the implementation strategy, including system components, implementation phases, project structure, and technical requirements.

#### rag_strategy.md
Details the approach for RAG testing and unstructured data generation, including use cases, data enhancement recommendations, unstructured data types, and implementation approach.

## Reorganization Changes

The memory bank reorganization involved:

1. **Cleaning up core files**:
   - Reorganized activeContext.md into clear sections
   - Fixed formatting inconsistencies in decisionLog.md
   - Reorganized progress.md to clearly separate task categories

2. **Consolidating technical documentation**:
   - Created architecture.md with comprehensive architecture documentation
   - Created data_model.md with complete data model documentation
   - Created implementation_strategy.md with implementation approach and plan
   - Created rag_strategy.md with RAG testing and unstructured data approach

3. **Adding this guide**:
   - Created README.md to explain the memory bank organization

## How to Use the Memory Bank

1. Start with **productContext.md** to understand the project goals and high-level architecture
2. Check **activeContext.md** to see the current focus and open questions
3. Review **progress.md** to understand what has been completed and what's currently in progress
4. Consult **decisionLog.md** to understand key architectural decisions
5. Refer to the consolidated technical documentation for detailed information on specific aspects of the project

## Maintenance Guidelines

1. Keep **activeContext.md** and **progress.md** updated as the project evolves
2. Add new decisions to **decisionLog.md** as they are made
3. Update the consolidated technical documentation when significant changes occur
4. Maintain consistent formatting and organization across all files