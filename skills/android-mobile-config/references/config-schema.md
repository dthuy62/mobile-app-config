# Config Schema

The default config file is `android-mobile-config.json` in the Android project root.

```json
{
  "module": "app",
  "dimension": "environment",
  "flavors": {
    "dev": {
      "applicationIdSuffix": ".dev",
      "appName": "[DEV] Career Ops",
      "buildConfigFields": {
        "CAREER_OPS_ENVIRONMENT": "dev",
        "CAREER_OPS_DEFAULT_BASE_URL": "http://10.0.2.2:3000"
      }
    },
    "prod": {
      "applicationIdSuffix": "",
      "appName": "Career Ops",
      "buildConfigFields": {
        "CAREER_OPS_ENVIRONMENT": "prod",
        "CAREER_OPS_DEFAULT_BASE_URL": ""
      }
    }
  },
  "networkSecurity": {
    "enabled": false
  },
  "assets": {
    "enabled": false,
    "sourceIcon": "",
    "generateLauncherIcon": true,
    "generateAdaptiveIcon": true,
    "generateSplashIcon": true,
    "generateNotificationIcon": true
  }
}
```

Commands auto-create this file when missing. Existing files are not rewritten unless `init --force` is used.

