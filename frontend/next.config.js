/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  // Static export — no server-side rendering, no rewrites needed.
  // Frontend uses relative URLs (/v1/chat) which proxy.js handles.
  // Images are unoptimized in static export mode.
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
