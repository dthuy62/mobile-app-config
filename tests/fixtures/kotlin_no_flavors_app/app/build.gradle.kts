plugins {
  id("com.android.application")
}

android {
  namespace = "com.example.noflavors"
  compileSdk = 35

  defaultConfig {
    applicationId = "com.example.noflavors"
    minSdk = 24
    targetSdk = 35
    versionCode = 1
    versionName = "1.0"
  }

  signingConfigs {
    create("debugConfig") {
      storePassword = "android"
    }
  }

  buildTypes {
    debug {
      signingConfig = signingConfigs.getByName("debugConfig")
    }
    release {
      isMinifyEnabled = false
    }
  }
}

dependencies {
  implementation("androidx.core:core-ktx:1.13.1")
}

