/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
		optimizePackageImports: ['better-auth']
	}
}

module.exports = nextConfig
