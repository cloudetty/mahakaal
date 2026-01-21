import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
    appId: 'com.mahakaal.app',
    appName: 'Mahakaal',
    webDir: 'dist',
    bundledWebRuntime: false,
    server: {
        androidScheme: 'https',
        iosScheme: 'capacitor'
    }
};

export default config;
