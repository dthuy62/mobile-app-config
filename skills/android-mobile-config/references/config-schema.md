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
  "packageName": {
    "applicationId": "",
    "syncSourcePackages": true
  },
  "firebase": {
    "enabled": false,
    "mode": "single",
    "project": "",
    "createApps": false,
    "flavors": {
      "dev": {
        "project": ""
      },
      "prod": {
        "project": ""
      }
    }
  },
  "assets": {
    "enabled": false,
    "sourceIcon": "",
    "types": ["app-icons"],
    "appIcons": {
      "image": "",
      "backgroundColor": "#FFFFFF",
      "monochromeImage": ""
    },
    "splashScreens": {
      "image": "",
      "backgroundColor": "#FFFFFF",
      "darkImage": "",
      "darkBackgroundColor": ""
    },
    "generateLauncherIcon": true,
    "generateAdaptiveIcon": true,
    "generateSplashIcon": true,
    "generateNotificationIcon": true
  }
}
```

Commands auto-create this file when missing. Existing files are not rewritten unless `init --force` is used.

Firebase single-project mode:

```bash
android-mobile-config firebase --mode single --project my-firebase
```

Firebase per-flavor mode:

```bash
android-mobile-config firebase --mode per-flavor --flavor dev=my-dev --flavor prod=my-prod
```

Package name sync:

```bash
android-mobile-config package-name --application-id com.aistudio.taskarena.kymzap
```

Typed asset generation:

```bash
android-mobile-config assets --type app-icons --image branding/logo.png
android-mobile-config assets --type splash-screens --image branding/splash.png
android-mobile-config assets --type all --image branding/logo.png
```
