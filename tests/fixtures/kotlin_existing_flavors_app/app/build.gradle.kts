plugins {
  id("com.android.application")
}

android {
  namespace = "com.example.existing"
  compileSdk = 35

  defaultConfig {
    applicationId = "com.example.existing"
    minSdk = 24
    targetSdk = 35
    versionCode = 1
    versionName = "1.0"
  }

  flavorDimensions += "evironment"

  productFlavors {
    create("dev") {
      dimension = "evironment"
      applicationIdSuffix = ".dev"
      buildConfigField("String", "CAREER_OPS_ENVIRONMENT", "\"dev\"")
      buildConfigField("String", "CAREER_OPS_DEFAULT_BASE_URL", "\"http://10.0.2.2:3000\"")
    }
    create("prod") {
      dimension = "evironment"
      buildConfigField("String", "CAREER_OPS_ENVIRONMENT", "\"prod\"")
      buildConfigField("String", "CAREER_OPS_DEFAULT_BASE_URL", "\"\"")
    }
    create("staging") {
      dimension = "evironment"
      applicationIdSuffix = ".staging"
      buildConfigField("String", "CUSTOM_FIELD", "\"keep-me\"")
    }
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

