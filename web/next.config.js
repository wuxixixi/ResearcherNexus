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

  eslint: {
    // 在构建时忽略ESLint错误
    ignoreDuringBuilds: true,
  },
  typescript: {
    // 在构建时忽略TypeScript错误（如果需要）
    // ignoreBuildErrors: true,
  },
};

export default config;
