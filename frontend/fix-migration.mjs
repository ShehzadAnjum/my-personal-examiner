import { Pool } from '@neondatabase/serverless';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const connectionString = "postgresql://neondb_owner:npg_cAhdU9H2Zteo@ep-summer-salad-ad6d95d6-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require";

const pool = new Pool({
  connectionString,
  max: 1,
});

async function fixSchema() {
  try {
    console.log('🔧 Fixing Better Auth schema...');

    const sql = readFileSync(join(__dirname, 'fix-schema.sql'), 'utf8');
    await pool.query(sql);

    console.log('✅ Schema fixed successfully!');
  } catch (error) {
    console.error('❌ Fix failed:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

fixSchema();
