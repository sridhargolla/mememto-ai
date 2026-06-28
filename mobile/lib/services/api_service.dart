import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

class ApiService with ChangeNotifier {
  static const String baseUrl = 'http://10.0.2.2:8000'; // For Android emulator
  static const String localBaseUrl = 'http://localhost:8000'; // For physical device
  
  String? _token;
  Map<String, dynamic>? _aiStatus;
  bool _isOffline = false;

  String? get token => _token;
  Map<String, dynamic>? get aiStatus => _aiStatus;
  bool get isOffline => _isOffline;

  ApiService() {
    _loadToken();
    _checkAIStatus();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    notifyListeners();
  }

  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    _token = token;
    notifyListeners();
  }

  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    _token = null;
    notifyListeners();
  }

  Future<void> _checkAIStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/status'),
      ).timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        _aiStatus = jsonDecode(response.body);
        _isOffline = false;
      } else {
        _isOffline = true;
      }
    } catch (e) {
      _isOffline = true;
      debugPrint('AI Status check failed: $e');
    }
    notifyListeners();
  }

  Map<String, String> get headers {
    return {
      'Content-Type': 'application/json',
      if (_token != null) 'Authorization': 'Bearer $_token',
    };
  }

  Future<http.Response> post(String endpoint, Map<String, dynamic> body) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: headers,
        body: jsonEncode(body),
      ).timeout(const Duration(seconds: 30));
      _isOffline = false;
      notifyListeners();
      return response;
    } catch (e) {
      _isOffline = true;
      notifyListeners();
      rethrow;
    }
  }

  Future<http.Response> get(String endpoint) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: headers,
      ).timeout(const Duration(seconds: 30));
      _isOffline = false;
      notifyListeners();
      return response;
    } catch (e) {
      _isOffline = true;
      notifyListeners();
      rethrow;
    }
  }

  Future<http.Response> uploadFile(String endpoint, String filePath, String filename) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl$endpoint'));
      request.headers['Authorization'] = 'Bearer $_token';
      request.files.add(await http.MultipartFile.fromPath('file', filePath, filename: filename));
      
      final response = await request.send().timeout(const Duration(seconds: 120));
      final responseData = await http.Response.fromStream(response);
      
      _isOffline = false;
      notifyListeners();
      return responseData;
    } catch (e) {
      _isOffline = true;
      notifyListeners();
      rethrow;
    }
  }
}
