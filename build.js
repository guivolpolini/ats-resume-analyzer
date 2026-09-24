const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Se estiver na raiz, entra na pasta frontend
if (fs.existsSync('frontend') && fs.statSync('frontend').isDirectory()) {
  process.chdir('frontend');
}

console.log('--- [Build Script] Instalando dependências do frontend ---');
execSync('npm install', { stdio: 'inherit' });

console.log('--- [Build Script] Compilando frontend Vite ---');
execSync('npm run build', { stdio: 'inherit' });

// Garante que a pasta dist exista tanto dentro de frontend quanto na raiz
const currentDist = path.resolve('dist');
const parentDist = path.resolve('..', 'dist');

if (fs.existsSync(currentDist) && !fs.existsSync(parentDist)) {
  try {
    fs.cpSync(currentDist, parentDist, { recursive: true });
  } catch (err) {
    console.warn('Aviso ao sincronizar pasta dist:', err.message);
  }
}

console.log('--- [Build Script] Build concluído com sucesso ---');
