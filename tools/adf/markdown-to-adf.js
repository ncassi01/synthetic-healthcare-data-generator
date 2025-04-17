#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Check if required arguments are provided
if (process.argv.length < 3) {
  console.log('Usage: node markdown-to-adf.js <input.md> [output.json]');
  console.log('If output file is not specified, it will use the input filename with .json extension');
  process.exit(1);
}

// Get input and output file paths
const inputFile = process.argv[2];
const outputFile = process.argv.length > 3 ? process.argv[3] : inputFile.replace(/\.md$/, '.json');

// Check if input file exists
if (!fs.existsSync(inputFile)) {
  console.error(`Error: Input file '${inputFile}' does not exist.`);
  process.exit(1);
}

// Read markdown content
const markdown = fs.readFileSync(inputFile, 'utf8');

// Convert markdown to ADF
const adf = parseMarkdownToADF(markdown);

// Write ADF to output file
fs.writeFileSync(outputFile, JSON.stringify(adf, null, 2));
console.log(`Successfully converted '${inputFile}' to ADF format at '${outputFile}'`);

/**
 * Converts markdown text to ADF format
 * @param {string} markdown - The markdown text to convert
 * @returns {Object} - The ADF document
 */
function parseMarkdownToADF(markdown) {
  // Initialize ADF document
  const adf = {
    version: 1,
    type: 'doc',
    content: []
  };
  
  // Split markdown into lines
  const lines = markdown.split('\n');
  
  // Process lines
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    
    // Skip empty lines
    if (!line) {
      i++;
      continue;
    }
    
    // Headings
    if (line.startsWith('#')) {
      const match = line.match(/^(#{1,6})\s+(.+)$/);
      if (match) {
        const level = match[1].length;
        const text = match[2];
        adf.content.push({
          type: 'heading',
          attrs: {
            level
          },
          content: [
            {
              type: 'text',
              text
            }
          ]
        });
      }
      i++;
      continue;
    }
    
    // Code blocks
    if (line.startsWith('```')) {
      const language = line.substring(3).trim();
      let codeContent = '';
      i++;
      
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeContent += lines[i] + '\n';
        i++;
      }
      
      adf.content.push({
        type: 'codeBlock',
        attrs: {
          language: language || 'plain'
        },
        content: [
          {
            type: 'text',
            text: codeContent
          }
        ]
      });
      
      i++; // Skip the closing ```
      continue;
    }
    
    // Bullet lists
    if (line.match(/^[-*]\s+/)) {
      const bulletList = {
        type: 'bulletList',
        content: []
      };
      
      while (i < lines.length && lines[i].trim().match(/^[-*]\s+/)) {
        const text = lines[i].trim().replace(/^[-*]\s+/, '');
        bulletList.content.push({
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: parseInlineMarkdown(text)
            }
          ]
        });
        i++;
      }
      
      adf.content.push(bulletList);
      continue;
    }
    
    // Numbered lists
    if (line.match(/^\d+\.\s+/)) {
      const orderedList = {
        type: 'orderedList',
        content: []
      };
      
      while (i < lines.length && lines[i].trim().match(/^\d+\.\s+/)) {
        const text = lines[i].trim().replace(/^\d+\.\s+/, '');
        orderedList.content.push({
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: parseInlineMarkdown(text)
            }
          ]
        });
        i++;
      }
      
      adf.content.push(orderedList);
      continue;
    }
    
    // Paragraphs (default)
    adf.content.push({
      type: 'paragraph',
      content: parseInlineMarkdown(line)
    });
    
    i++;
  }
  
  return adf;
}

/**
 * Parses inline markdown formatting
 * @param {string} text - The text to parse
 * @returns {Array} - Array of ADF content nodes
 */
function parseInlineMarkdown(text) {
  const content = [];
  
  // Process the text for inline formatting
  let currentIndex = 0;
  let currentText = '';
  
  // Helper function to add accumulated text
  function addCurrentText() {
    if (currentText) {
      content.push({
        type: 'text',
        text: currentText
      });
      currentText = '';
    }
  }
  
  while (currentIndex < text.length) {
    // Bold (**text**)
    if (text.substr(currentIndex, 2) === '**' && 
        text.indexOf('**', currentIndex + 2) !== -1) {
      
      addCurrentText();
      
      const startIndex = currentIndex + 2;
      const endIndex = text.indexOf('**', startIndex);
      const boldText = text.substring(startIndex, endIndex);
      
      content.push({
        type: 'text',
        text: boldText,
        marks: [
          {
            type: 'strong'
          }
        ]
      });
      
      currentIndex = endIndex + 2;
      continue;
    }
    
    // Italic (*text*)
    if (text[currentIndex] === '*' && 
        text.indexOf('*', currentIndex + 1) !== -1) {
      
      addCurrentText();
      
      const startIndex = currentIndex + 1;
      const endIndex = text.indexOf('*', startIndex);
      const italicText = text.substring(startIndex, endIndex);
      
      content.push({
        type: 'text',
        text: italicText,
        marks: [
          {
            type: 'em'
          }
        ]
      });
      
      currentIndex = endIndex + 1;
      continue;
    }
    
    // Inline code (`code`)
    if (text[currentIndex] === '`' && 
        text.indexOf('`', currentIndex + 1) !== -1) {
      
      addCurrentText();
      
      const startIndex = currentIndex + 1;
      const endIndex = text.indexOf('`', startIndex);
      const codeText = text.substring(startIndex, endIndex);
      
      content.push({
        type: 'text',
        text: codeText,
        marks: [
          {
            type: 'code'
          }
        ]
      });
      
      currentIndex = endIndex + 1;
      continue;
    }
    
    // Links [text](url)
    if (text[currentIndex] === '[' && 
        text.indexOf('](', currentIndex) !== -1 && 
        text.indexOf(')', text.indexOf('](', currentIndex)) !== -1) {
      
      addCurrentText();
      
      const textStartIndex = currentIndex + 1;
      const textEndIndex = text.indexOf('](', currentIndex);
      const linkText = text.substring(textStartIndex, textEndIndex);
      
      const urlStartIndex = textEndIndex + 2;
      const urlEndIndex = text.indexOf(')', urlStartIndex);
      const url = text.substring(urlStartIndex, urlEndIndex);
      
      content.push({
        type: 'text',
        text: linkText,
        marks: [
          {
            type: 'link',
            attrs: {
              href: url
            }
          }
        ]
      });
      
      currentIndex = urlEndIndex + 1;
      continue;
    }
    
    // Regular text
    currentText += text[currentIndex];
    currentIndex++;
  }
  
  // Add any remaining text
  addCurrentText();
  
  return content;
}