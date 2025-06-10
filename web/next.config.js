/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

import "./src/env.js";

/** @type {import("next").NextConfig} */

// ResearcherNexus leverages **Turbopack** during development for faster builds and a smoother developer experience.
// However, in production, **Webpack** is used instead.
//
// This decision is based on the current recommendation to avoid using Turbopack for critical projects, as it
// is still evolving and may not yet be fully stable for production environments.

const config = {
  // For development mode
  turbopack: {
    rules: {
      "*.md": {
        loaders: ["raw-loader"],
        as: "*.js",
      },
    },
  },

  // 添加开发环境允许的源
  allowedDevOrigins: [
    'http://172.16.128.43:3000',
    'http://localhost:3000'
  ],

  // For production mode
  webpack: (config) => {
    config.module.rules.push({
      test: /\.md$/,
      use: "raw-loader",
    });
    return config;
  },

  // ... rest of the configuration.
  output: "standalone",

  // 添加生产环境配置
  env: {
    NEXT_PUBLIC_API_URL: 'http://172.16.128.43:8000/api',
  },

  // 添加跨域配置
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ],
      },
    ]
  },

  // 添加重写规则
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://172.16.128.43:8000/api/:path*',
      },
    ]
  },

  eslint: {
    // Enable ESLint during builds
    ignoreDuringBuilds: false,
    // Only errors will fail the build, not warnings
    dirs: ['src'],
  },
  typescript: {
    // 在构建时忽略TypeScript错误（如果需要）
    // ignoreBuildErrors: true,
  },
};

export default config;
