import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<Map<String, dynamic>> _messages = [];
  bool _isTyping = false;

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
    }
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    setState(() {
      _messages.add({'role': 'user', 'content': message});
      _isTyping = true;
      _messageController.clear();
    });

    _scrollToBottom();

    try {
      final apiService = context.read<ApiService>();
      final response = await apiService.post('/chat', {
        'message': message,
      });

      if (response.statusCode == 200) {
        // Handle streaming response
        final lines = response.body.split('\n');
        String assistantMessage = '';

        for (final line in lines) {
          if (line.startsWith('data: ')) {
            final data = line.substring(6);
            try {
              final json = jsonDecode(data);
              if (json.containsKey('token')) {
                assistantMessage += json['token'];
                setState(() {
                  if (_messages.isNotEmpty && _messages.last['role'] == 'assistant') {
                    _messages.last['content'] = assistantMessage;
                  } else {
                    _messages.add({'role': 'assistant', 'content': assistantMessage});
                  }
                });
                _scrollToBottom();
              } else if (json['done'] == true) {
                break;
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      } else {
        setState(() {
          _messages.add({
            'role': 'assistant',
            'content': 'Error: Failed to get response from AI',
          });
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({
          'role': 'assistant',
          'content': 'Error: ${e.toString()}',
        });
      });
    } finally {
      setState(() {
        _isTyping = false;
      });
      _scrollToBottom();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: _messages.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.chat_bubble_outline,
                        size: 64,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Start a conversation',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Ask anything about your memories',
                        style: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length + (_isTyping ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (index == _messages.length && _isTyping) {
                      return const Padding(
                        padding: EdgeInsets.all(16),
                        child: Center(
                          child: CircularProgressIndicator(),
                        ),
                      );
                    }

                    final message = _messages[index];
                    final isUser = message['role'] == 'user';

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Row(
                        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                        children: [
                          Container(
                            constraints: BoxConstraints(
                              maxWidth: MediaQuery.of(context).size.width * 0.8,
                            ),
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: isUser
                                  ? Theme.of(context).colorScheme.primary
                                  : Colors.grey[800],
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              message['content'],
                              style: TextStyle(
                                color: isUser ? Colors.white : Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
        ),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 4,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _messageController,
                  decoration: InputDecoration(
                    hintText: 'Type your message...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 12,
                    ),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 12),
              IconButton(
                onPressed: _isTyping ? null : _sendMessage,
                icon: const Icon(Icons.send),
                style: IconButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.all(12),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
