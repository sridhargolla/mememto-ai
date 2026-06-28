# Memento AI - Android Mobile App

Offline-first personal AI memory engine for Android devices.

## Features

- **Chat**: Interact with your personal AI assistant
- **Upload**: Process documents (PDF, TXT, PNG, JPG, WAV, MP3) to extract memories
- **Memories**: View and search your extracted memories
- **Settings**: View AI status and manage your profile
- **Offline Support**: Works without internet connection
- **Local AI**: Communicates with local Memento AI backend (no cloud APIs)

## Requirements

- Flutter SDK 3.0+
- Android SDK 21+ (Android 5.0+)
- Local Memento AI backend running on the same network

## Installation

### Prerequisites

1. Install Flutter SDK: https://flutter.dev/docs/get-started/install
2. Install Android Studio with Android SDK
3. Enable developer mode on your Android device

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd memento-ai/mobile
```

2. Install dependencies:
```bash
flutter pub get
```

3. Connect your Android device or start an emulator:
```bash
flutter devices
```

4. Run the app:
```bash
flutter run
```

## Backend Configuration

The mobile app communicates with the local Memento AI backend. By default, it uses:
- **Emulator**: `http://10.0.2.2:8000` (Android emulator localhost)
- **Physical Device**: `http://localhost:8000` (requires backend on same network)

To configure the backend URL, edit `lib/services/api_service.dart`:
```dart
static const String baseUrl = 'http://YOUR_BACKEND_IP:8000';
```

## Building APK

### Debug APK
```bash
flutter build apk --debug
```
Output: `build/app/outputs/flutter-apk/app-debug.apk`

### Release APK
```bash
flutter build apk --release
```
Output: `build/app/outputs/flutter-apk/app-release.apk`

### App Bundle (for Play Store)
```bash
flutter build appbundle --release
```
Output: `build/app/outputs/bundle/release/app-release.aab`

## Permissions

The app requires the following permissions:
- `INTERNET`: Communicate with local backend
- `READ_EXTERNAL_STORAGE`: Select files for upload
- `WRITE_EXTERNAL_STORAGE`: Save downloaded files
- `READ_MEDIA_*`: Access media files for upload (Android 13+)

## Architecture

```
lib/
├── main.dart              # App entry point
├── screens/               # UI screens
│   ├── login_screen.dart
│   ├── home_screen.dart
│   ├── chat_screen.dart
│   ├── upload_screen.dart
│   ├── memories_screen.dart
│   └── settings_screen.dart
└── services/              # Business logic
    ├── api_service.dart   # HTTP communication
    └── auth_service.dart  # Authentication
```

## Offline Support

The app includes offline support:
- Local storage for authentication tokens
- Offline status indicator
- Graceful error handling when backend is unavailable
- Cached user data

## CPU/Local AI Status

The Settings screen displays real-time AI status:
- AI Runtime (llama.cpp)
- Device (CPU)
- Internet status (Offline)
- Current model
- External API calls (0)

## Security

- All communication with local backend only
- No cloud AI APIs
- JWT token authentication
- Local storage for credentials

## Troubleshooting

### Backend Not Connecting
- Ensure Memento AI backend is running
- Check network configuration
- Verify backend URL in `api_service.dart`
- For physical devices, ensure both device and computer are on same network

### File Upload Failing
- Check file permissions
- Ensure file format is supported
- Verify file size (max 50MB for async upload)
- Check backend logs for errors

### Build Errors
- Run `flutter clean`
- Run `flutter pub get`
- Ensure Flutter SDK is properly installed
- Check Android SDK installation

## Development

### Running Tests
```bash
flutter test
```

### Code Analysis
```bash
flutter analyze
```

### Format Code
```bash
flutter format .
```

## License

GNU Affero General Public License v3.0
