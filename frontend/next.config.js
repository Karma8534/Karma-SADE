const crypto = require('node:crypto')
const fs = require('node:fs')
const path = require('node:path')

function resolveStableBuildId() {
  const roots = [
    path.join(__dirname, 'src'),
    path.join(__dirname, 'package.json'),
    path.join(__dirname, 'package-lock.json'),
    path.join(__dirname, 'postcss.config.js'),
    path.join(__dirname, 'tailwind.config.ts'),
    path.join(__dirname, 'tsconfig.json'),
    __filename,
  ]
  const hash = crypto.createHash('sha256')

  function addFile(filePath) {
    const rel = path.relative(__dirname, filePath).replace(/\\/g, '/')
    hash.update(rel)
    hash.update('\n')
    hash.update(fs.readFileSync(filePath))
    hash.update('\n')
  }

  function walk(entryPath) {
    const stat = fs.statSync(entryPath)
    if (stat.isDirectory()) {
      for (const child of fs.readdirSync(entryPath).sort()) {
        walk(path.join(entryPath, child))
      }
      return
    }
    addFile(entryPath)
  }

  for (const root of roots) {
    if (fs.existsSync(root)) {
      walk(root)
    }
  }

  return hash.digest('hex').slice(0, 20)
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  assetPrefix: './',
  images: { unoptimized: true },
  generateBuildId: async () => resolveStableBuildId(),
}

module.exports = nextConfig
