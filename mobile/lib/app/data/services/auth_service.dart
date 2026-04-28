import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';

class AuthService extends GetxService {
  final _storage = GetStorage();
  
  final _isLoggedIn = false.obs;
  bool get isLoggedIn => _isLoggedIn.value;
  
  final _userName = Rx<String?>(null);
  String? get userName => _userName.value;
  
  final _userEmail = Rx<String?>(null);
  String? get userEmail => _userEmail.value;

  static const _keyLoggedIn = 'is_logged_in';
  static const _keyUserName = 'user_name';
  static const _keyUserEmail = 'user_email';

  Future<AuthService> init() async {
    _isLoggedIn.value = _storage.read(_keyLoggedIn) ?? false;
    _userName.value = _storage.read(_keyUserName);
    _userEmail.value = _storage.read(_keyUserEmail);
    return this;
  }

  void login(String name, String email) {
    _isLoggedIn.value = true;
    _userName.value = name;
    _userEmail.value = email;
    
    _storage.write(_keyLoggedIn, true);
    _storage.write(_keyUserName, name);
    _storage.write(_keyUserEmail, email);
  }

  void logout() {
    _isLoggedIn.value = false;
    _userName.value = null;
    _userEmail.value = null;
    
    _storage.write(_keyLoggedIn, false);
    _storage.remove(_keyUserName);
    _storage.remove(_keyUserEmail);
  }
}
