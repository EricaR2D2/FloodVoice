import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  turbopack: {
    // Explicitly set workspace root to this project directory,
    // avoiding confusion with the stray package-lock.json at C:\Users\ricar\
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
