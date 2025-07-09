
import path from 'path';
import { defineConfig } from 'vite';
// Fix: Define __dirname for ES module scope
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename); // __dirname is now frontend/Command-Console

export default defineConfig(({ mode }) => {
    return {
      // Set Vite's root to the actual project root where index.html is located
      root: path.resolve(__dirname, '../..'), 
      // Assuming your public assets (like header.png) are in frontend/Command-Console/public
      // This path is relative to the new 'root' defined above.
      publicDir: 'frontend/Command-Console/public',
      resolve: {
        alias: {
          // '@' will resolve to the 'frontend/Command-Console' directory
          '@': path.resolve(__dirname, '.'), 
        }
      },
      build: {
        // Output the build to 'dist' in the actual project root
        outDir: path.resolve(__dirname, '../../dist'), 
      }
    };
});