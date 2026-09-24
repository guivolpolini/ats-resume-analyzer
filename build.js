const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Localiza a pasta frontend independente de onde o script foi chamado
let frontendDir = null;
if (fs.existsSync('frontend') && fs.statSync('frontend').isDirectory()) {
  frontendDir = path.resolve('frontend');
} else if (fs.existsSync('../frontend') && fs.statSync('../frontend').isDirectory()) {
  frontendDir = path.resolve('../frontend');
}

if (!frontendDir) {
  console.error('Erro: Pasta frontend não encontrada.');
  process.exit(1);
}

console.log('--- [Build Script] Entrando no diretório:', frontendDir);
process.chdir(frontendDir);

console.log('--- [Build Script] Instalando dependências do frontend ---');
execSync('npm install', { stdio: 'inherit' });

console.log('--- [Build Script] Compilando frontend Vite ---');
execSync('npm run build', { stdio: 'inherit' });

// Sincroniza dist para todos os locais necessários
const distDir = path.resolve('dist');
const targets = [
  path.resolve('..', 'dist'),
  path.resolve('..', 'backend', 'dist'),
  path.resolve('..', 'backend', 'app', 'static')
];

for (const target of targets) {
  try {
    fs.cpSync(distDir, target, { recursive: true });
    console.log('--- [Build Script] Sincronizado dist para:', target);
  } catch (err) {
    console.warn('Aviso ao sincronizar pasta dist:', err.message);
  }
}

console.log('--- [Build Script] Build concluído com sucesso ---');
