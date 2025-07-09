// backend/routes/memoryRoutes.js
import express from 'express';
import { logger } from '../utils/logger.js';
// Supabase client will be passed or initialized globally in main gatekeeper.js

export default function(supabaseAlden) {
  const router = express.Router();

  // GET /api/memory_items - Get memory items (from Alden DB)
  router.get('/', async (req, res) => {
      const { source: querySource, type: queryItemType, q: searchQuery, limit = 50, offset = 0 } = req.query;
      const parsedLimit = parseInt(limit, 10);
      const parsedOffset = parseInt(offset, 10);

      if (supabaseAlden) {
          try {
              let query = supabaseAlden
                  .from('chunks') // Assuming 'chunks' is the primary table for memory items
                  .select(`
                      id, 
                      content, 
                      created_at, 
                      documents!inner (id, title, source, created_at, metadata) 
                  `) // Use !inner to ensure documents exist
                  .range(parsedOffset, parsedOffset + parsedLimit - 1)
                  .order('created_at', { referencedTable: 'chunks', ascending: false });


              if (searchQuery) {
                  // Search in chunk content OR document title
                  query = query.or(`content.ilike.%${searchQuery}%,documents.title.ilike.%${searchQuery}%`);
              }
              
              // Filtering by source or type would depend on how these are stored.
              // Example: if documents.source contains 'AldenRAG' or 'MCPWebcrawl'
              if (querySource === 'AldenRAG') {
                  query = query.eq('documents.source_identifier_column', 'alden_source_value'); // Replace with actual column and value
              } else if (querySource === 'MCPWebcrawl') {
                  query = query.eq('documents.source_identifier_column', 'mcp_source_value'); // Replace
              }

              // Example: if documents.metadata contains a type field (e.g., documents.metadata->>type)
              if (queryItemType) {
                   query = query.eq('documents.metadata->>type', queryItemType); // JSONB query
              }


              const { data: dbItems, error, count } = await query;
              if (error) throw error;

              const memoryItems = (dbItems || []).map(item => {
                  const doc = item.documents; // This is an object due to !inner
                  let itemSource = 'AldenRAG'; // Default or derive from doc.source
                  let itemType = 'Text Chunk'; // Default or derive

                  if (doc && doc.source) {
                      if (doc.source.toLowerCase().includes('mcp') || doc.source.startsWith('http')) {
                          itemSource = 'MCPWebcrawl';
                      }
                  }
                  if (doc && doc.metadata && doc.metadata.type) {
                      itemType = doc.metadata.type;
                  } else if (doc && doc.title && doc.title.toLowerCase().endsWith('.pdf')) {
                      itemType = 'PDF Document';
                  } else if (doc && doc.source && doc.source.startsWith('http')) {
                      itemType = 'Web Page Content';
                  }
                  
                  return {
                      id: item.id,
                      source: itemSource,
                      type: itemType,
                      description: `${doc ? doc.title || 'Untitled Document' : 'N/A'}: ${item.content.substring(0, 100)}...`,
                      size: `${item.content.length} chars`,
                      timestamp: new Date(item.created_at).toISOString(),
                      tags: doc?.metadata?.tags || [], // Assuming tags are in doc.metadata.tags
                  };
              });
              logger.debug('Memory items fetched from Supabase Alden DB', 'MemoryRoutes', { count: memoryItems.length });
              return res.json({ data: memoryItems, total: count /* May need separate count query */ });
          } catch (dbError) {
              logger.error('Supabase (Alden DB) error fetching memory items', 'MemoryRoutes', { error: dbError.message });
              return res.json({ data: [], total: 0 }); // Fallback to empty array
          }
      }
      logger.warn('/api/memory_items: Alden Supabase not configured. Returning empty data.', 'MemoryRoutes');
      res.json({data: [], total: 0 }); // Fallback if Supabase not configured
  });
  return router;
}
