plugins {
  id("com.android.application")
}

android {
  namespace = "com.example.fixture"
  compileSdk = 35

  defaultConfig {
    applicationId = "com.example.fixture"
    minSdk = 24
    targetSdk = 35
    versionCode = 1
    versionName = "1.0"
  }

  buildTypes {
    debug {}
    release {
      isMinifyEnabled = false
    }
  }
}

dependencies {
}

