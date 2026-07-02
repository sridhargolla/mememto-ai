import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isSignup = false;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final authService = context.read<AuthService>();
    final apiService = context.read<ApiService>();

    bool success;
    if (_isSignup) {
      success = await authService.signup(
        _emailController.text,
        _emailController.text,
        _passwordController.text,
      );
    } else {
      success = await authService.login(
        _emailController.text,
        _passwordController.text,
      );
    }

    setState(() {
      _isLoading = false;
    });

    if (success) {
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } else {
      setState(() {
        _errorMessage = apiService.isOffline
          ? 'Cannot connect to server. Please ensure backend is running.'
          : 'Invalid credentials';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<ApiService>(
        builder: (context, apiService, child) {
          return Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primary,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Icon(
                        Icons.psychology,
                        size: 60,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Title
                    Text(
                      'Memento AI',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Offline Personal Memory Engine',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                    const SizedBox(height: 48),

                    // AI Status Indicator
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: apiService.isOffline
                          ? Colors.red.withOpacity(0.1)
                          : Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: apiService.isOffline ? Colors.red : Colors.green,
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            apiService.isOffline ? Icons.wifi_off : Icons.wifi,
                            color: apiService.isOffline ? Colors.red : Colors.green,
                            size: 16,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            apiService.isOffline ? 'Backend Offline' : 'Backend Online',
                            style: TextStyle(
                              color: apiService.isOffline ? Colors.red : Colors.green,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Name field (signup only)
                    if (_isSignup)
                      TextFormField(
                        controller: _emailController,
                        decoration: const InputDecoration(
                          labelText: 'Name',
                          prefixIcon: Icon(Icons.person),
                          border: OutlineInputBorder(),
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your name';
                          }
                          return null;
                        },
                      ),
                    if (_isSignup) const SizedBox(height: 16),

                    // Email field
                    TextFormField(
                      controller: _emailController,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        prefixIcon: Icon(Icons.email),
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.emailAddress,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your email';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // Password field
                    TextFormField(
                      controller: _passwordController,
                      decoration: const InputDecoration(
                        labelText: 'Password',
                        prefixIcon: Icon(Icons.lock),
                        border: OutlineInputBorder(),
                      ),
                      obscureText: true,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        if (value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),

                    // Error message
                    if (_errorMessage != null)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 16),
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(color: Colors.red),
                        ),
                      ),

                    // Submit button
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _submit,
                        child: _isLoading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : Text(_isSignup ? 'Sign Up' : 'Login'),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Toggle signup/login
                    TextButton(
                      onPressed: () {
                        setState(() {
                          _isSignup = !_isSignup;
                          _errorMessage = null;
                        });
                      },
                      child: Text(
                        _isSignup
                            ? 'Already have an account? Login'
                            : 'Don\'t have an account? Sign Up',
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
