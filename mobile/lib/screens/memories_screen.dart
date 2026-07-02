import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import '../services/api_service.dart';

class MemoriesScreen extends StatefulWidget {
  const MemoriesScreen({super.key});

  @override
  State<MemoriesScreen> createState() => _MemoriesScreenState();
}

class _MemoriesScreenState extends State<MemoriesScreen> {
  List<Map<String, dynamic>> _memories = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadMemories();
  }

  Future<void> _loadMemories() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final response = await apiService.get('/memories?limit=100');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _memories = List<Map<String, dynamic>>.from(data);
        });
      } else {
        setState(() {
          _errorMessage = 'Failed to load memories';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadMemories,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Your Memories',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Text(
                  '${_memories.length} memories',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _errorMessage != null
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.error_outline,
                                size: 64,
                                color: Colors.grey[600],
                              ),
                              const SizedBox(height: 16),
                              Text(
                                _errorMessage!,
                                style: TextStyle(
                                  color: Colors.grey[600],
                                ),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: _loadMemories,
                                child: const Text('Retry'),
                              ),
                            ],
                          ),
                        )
                      : _memories.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.psychology_outlined,
                                    size: 64,
                                    color: Colors.grey[600],
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'No memories yet',
                                    style: TextStyle(
                                      color: Colors.grey[600],
                                      fontSize: 18,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Upload documents to extract memories',
                                    style: TextStyle(
                                      color: Colors.grey[500],
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            )
                          : ListView.builder(
                              itemCount: _memories.length,
                              itemBuilder: (context, index) {
                                final memory = _memories[index];
                                return Card(
                                  margin: const EdgeInsets.only(bottom: 12),
                                  child: Padding(
                                    padding: const EdgeInsets.all(16),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          children: [
                                            _getTypeIcon(memory['type'] ?? 'memory'),
                                            const SizedBox(width: 8),
                                            Expanded(
                                              child: Text(
                                                memory['title'] ?? 'Untitled',
                                                style: const TextStyle(
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 16,
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          memory['content'] ?? '',
                                          maxLines: 3,
                                          overflow: TextOverflow.ellipsis,
                                          style: TextStyle(
                                            color: Colors.grey[400],
                                          ),
                                        ),
                                        const SizedBox(height: 12),
                                        Wrap(
                                          spacing: 8,
                                          runSpacing: 8,
                                          children: [
                                            if (memory['tags'] != null)
                                              ...memory['tags'].toString().split(',').map((tag) {
                                                return Chip(
                                                  label: Text(tag.trim()),
                                                  backgroundColor: Colors.blue.withOpacity(0.1),
                                                  labelStyle: const TextStyle(fontSize: 12),
                                                );
                                              }).toList(),
                                          ],
                                        ),
                                        if (memory['source_file'] != null)
                                          Padding(
                                            padding: const EdgeInsets.only(top: 8),
                                            child: Row(
                                              children: [
                                                Icon(
                                                  Icons.description,
                                                  size: 14,
                                                  color: Colors.grey[600],
                                                ),
                                                const SizedBox(width: 4),
                                                Expanded(
                                                  child: Text(
                                                    memory['source_file'],
                                                    style: TextStyle(
                                                      color: Colors.grey[600],
                                                      fontSize: 12,
                                                    ),
                                                    overflow: TextOverflow.ellipsis,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                );
                              },
                            ),
            ),
          ],
        ),
      ),
    );
  }

  Icon _getTypeIcon(String type) {
    switch (type.toLowerCase()) {
      case 'person':
        return const Icon(Icons.person, color: Colors.purple, size: 20);
      case 'event':
        return const Icon(Icons.event, color: Colors.pink, size: 20);
      case 'experience':
        return const Icon(Icons.work, color: Colors.blue, size: 20);
      case 'project':
        return const Icon(Icons.rocket_launch, color: Colors.green, size: 20);
      case 'education':
        return const Icon(Icons.school, color: Colors.orange, size: 20);
      case 'skill':
        return const Icon(Icons.lightbulb, color: Colors.yellow, size: 20);
      default:
        return const Icon(Icons.psychology, color: Colors.grey, size: 20);
    }
  }
}
