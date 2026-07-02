import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  Map<String, dynamic>? _aiStatus;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAIStatus();
  }

  Future<void> _loadAIStatus() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = context.read<ApiService>();
      await apiService._checkAIStatus();
      setState(() {
        _aiStatus = apiService.aiStatus;
      });
    } catch (e) {
      debugPrint('Failed to load AI status: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authService = context.read<AuthService>();
    final apiService = context.read<ApiService>();

    return RefreshIndicator(
      onRefresh: _loadAIStatus,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // User Profile Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 32,
                      backgroundColor: Theme.of(context).colorScheme.primary,
                      child: Text(
                        authService.user?['name']?.substring(0, 1).toUpperCase() ?? 'U',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            authService.user?['name'] ?? 'User',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            authService.user?['email'] ?? '',
                            style: TextStyle(
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // AI Status Section
            Text(
              'AI Status',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildStatusRow(
                            '🤖',
                            'AI Runtime',
                            _aiStatus?['runtime'] ?? 'Loading...',
                          ),
                          const Divider(),
                          _buildStatusRow(
                            '💻',
                            'Device',
                            _aiStatus?['device'] ?? 'Loading...',
                          ),
                          const Divider(),
                          _buildStatusRow(
                            '🌐',
                            'Internet',
                            _aiStatus?['offline'] == true ? 'Offline' : 'Online',
                            valueColor: _aiStatus?['offline'] == true
                                ? Colors.green
                                : Colors.red,
                          ),
                          const Divider(),
                          _buildStatusRow(
                            '📦',
                            'Model',
                            _aiStatus?['model'] ?? 'Loading...',
                          ),
                          const Divider(),
                          _buildStatusRow(
                            '📡',
                            'External API Calls',
                            '${_aiStatus?['external_api_calls'] ?? 0}',
                            valueColor: Colors.green,
                          ),
                        ],
                      ),
              ),
            ),
            const SizedBox(height: 24),

            // Connection Status
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      apiService.isOffline ? Icons.wifi_off : Icons.wifi,
                      color: apiService.isOffline ? Colors.red : Colors.green,
                      size: 32,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            apiService.isOffline ? 'Backend Offline' : 'Backend Online',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            apiService.isOffline
                                ? 'Cannot connect to local AI server'
                                : 'Connected to local AI server',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // App Info
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'About Memento AI',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Version 1.0.0',
                      style: TextStyle(
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Offline-first personal AI memory engine',
                      style: TextStyle(
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 16),
                    Text(
                      'Features',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    _buildFeatureItem('✅ CPU-only inference'),
                    _buildFeatureItem('✅ Offline operation'),
                    _buildFeatureItem('✅ Local AI models'),
                    _buildFeatureItem('✅ No cloud APIs'),
                    _buildFeatureItem('✅ Private data storage'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Logout Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  authService.logout();
                  Navigator.pushReplacementNamed(context, '/');
                },
                icon: const Icon(Icons.logout),
                label: const Text('Logout'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusRow(
    String icon,
    String label,
    String value, {
    Color? valueColor,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Text(icon, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                color: Colors.grey[600],
              ),
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureItem(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Text(
        text,
        style: TextStyle(
          color: Colors.grey[600],
        ),
      ),
    );
  }
}
