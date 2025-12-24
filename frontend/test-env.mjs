// Quick test to see what env vars are loaded
import 'dotenv/config';

console.log('Environment Variables:');
console.log('GOOGLE_CLIENT_ID:', process.env.GOOGLE_CLIENT_ID);
console.log('GOOGLE_CLIENT_SECRET:', process.env.GOOGLE_CLIENT_SECRET);
console.log('Length of CLIENT_ID:', process.env.GOOGLE_CLIENT_ID?.length);
console.log('Has quotes?:', process.env.GOOGLE_CLIENT_ID?.includes('"'));
