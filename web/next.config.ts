import { withGluestackUI } from '@gluestack/ui-next-adapter';
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  transpilePackages: [
    'nativewind',
    'react-native-css-interop',
    '@gluestack-ui/core',
    '@gluestack-ui/utils',
    '@gluestack-ui/themed',
    '@gluestack-style/react',
    'react-native-web',
    'react-native-svg',
    'react-native-safe-area-context',
  ],
  webpack: (config) => {
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      'react-native$': 'react-native-web',
    };
    
    config.resolve.extensions = [
      '.web.js',
      '.web.jsx',
      '.web.ts',
      '.web.tsx',
      ...config.resolve.extensions,
    ];

    return config;
  },
};

export default withGluestackUI(nextConfig);