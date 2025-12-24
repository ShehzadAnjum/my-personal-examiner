import { Pool } from '@neondatabase/serverless';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Database connection from .env.local
const connectionString = "postgresql://neondb_owner:npg_cAhdU9H2Zteo@ep-summer-salad-ad6d95d6-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require";

const pool = new Pool({
  connectionString,
  max: 1,
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 30_000,
});

async function runMigration() {
  try {
    console.log('🔌 Connecting to Neon database...');

    // Read the SQL file
    const sqlPath = join(__dirname, 'better-auth-schema.sql');
    const sql = readFileSync(sqlPath, 'utf8');

    console.log('📝 Running migration...');

    // Run the SQL
    await pool.query(sql);

    console.log('✅ Migration completed successfully!');
    console.log('📋 Created tables: user, session, account, verification');

  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

runMigration();
