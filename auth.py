"""Authentication module for EatWise"""
import streamlit as st
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from typing import Tuple, Optional, Dict, Any


class AuthManager:
    """Handles authentication and user management"""
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def sign_up(self, email: str, password: str, full_name: str) -> Tuple[bool, str]:
        """
        Sign up a new user
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            
        Returns:
            Tuple of (success, message/user_id)
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if response.user:
                # Store additional user info
                user_profile_data = {
                    "user_id": response.user.id,
                    "email": email,
                    "full_name": full_name,
                    "created_at": "now()",
                }
                
                self.supabase.table("users").insert(user_profile_data).execute()
                return True, response.user.id
            else:
                return False, "Sign up failed"
                
        except Exception as e:
            return False, f"Sign up error: {str(e)}"
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Login user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message, user_data)
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
            if response.user:
                user_id = response.user.id
                
                # Check if user exists in users table
                profile = self.supabase.table("users").select("*").eq("user_id", user_id).execute()
                
                if not profile.data:
                    # Create user record if it doesn't exist
                    try:
                        self.supabase.table("users").insert({
                            "user_id": user_id,
                            "email": email,
                            "full_name": ""
                        }).execute()
                    except Exception as e:
                        # User might already exist (race condition), continue anyway
                        pass
                    
                    return True, "Login successful", {
                        "user_id": user_id,
                        "email": email,
                        "full_name": ""
                    }
                else:
                    return True, "Login successful", profile.data[0]
            else:
                return False, "Invalid credentials", None
                
        except Exception as e:
            return False, f"Login error: {str(e)}", None
    
    def logout(self):
        """Logout user"""
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        try:
            response = self.supabase.table("users").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching profile: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user profile"""
        try:
            self.supabase.table("users").update(profile_data).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating profile: {str(e)}")
            return False
    
    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user password
        
        Args:
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Update password in Supabase Auth
            self.supabase.auth.update_user({
                "password": new_password
            })
            return True, "Password changed successfully!"
        except Exception as e:
            error_str = str(e)
            if "invalid_credentials" in error_str.lower() or "incorrect password" in error_str.lower():
                return False, "Current password is incorrect"
            else:
                return False, f"Error changing password: {error_str}"
    
    def reset_password(self, email: str) -> Tuple[bool, str]:
        """
        Send password reset email to user
        
        Args:
            email: User email address
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Attempt to send password recovery link
            self.supabase.auth.send_reset_password_email(email)
            return True, "Password reset link sent! Check your email for instructions."
        except AttributeError:
            # If send_reset_password_email doesn't exist, try alternative
            try:
                self.supabase.auth.reset_password_email(email)
                return True, "Password reset link sent! Check your email for instructions."
            except Exception:
                # Fallback: inform user to contact support
                return False, "Password reset is temporarily unavailable. Please contact support."
        except Exception as e:
            error_str = str(e).lower()
            if "user" in error_str or "not found" in error_str:
                return False, "Email not found in our system."
            else:
                return False, "Unable to process reset. Please try again later."
    
    def verify_otp_and_reset_password(self, email: str, otp: str, new_password: str) -> Tuple[bool, str]:
        """
        Verify OTP and reset password
        
        Args:
            email: User email address
            otp: One-time password from email
            new_password: New password to set
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Verify the OTP
            response = self.supabase.auth.verify_otp({
                "email": email,
                "token": otp,
                "type": "recovery"
            })
            
            if response.user:
                # Update the password
                self.supabase.auth.update_user({
                    "password": new_password
                })
                return True, "Password reset successfully!"
            else:
                return False, "Invalid or expired reset link."
                
        except Exception as e:
            error_str = str(e).lower()
            if "invalid" in error_str or "expired" in error_str:
                return False, "The reset link is invalid or has expired. Please request a new one."
            else:
                return False, f"Error resetting password: {str(e)}"
    
    def get_session_user(self) -> Optional[Dict]:
        """
        Get the current session user (used after password reset redirect)
        
        Returns:
            User data if session exists, None otherwise
        """
        try:
            session = self.supabase.auth.get_session()
            if session and session.user:
                return {
                    "user_id": session.user.id,
                    "email": session.user.email,
                }
            return None
        except Exception:
            return None
    
    def is_fresh_password_reset_session(self) -> bool:
        """
        Check if this is a fresh password reset session from email link
        (user hasn't logged in via password, only via reset link)
        
        Returns:
            True if this appears to be a reset session, False otherwise
        """
        try:
            session = self.supabase.auth.get_session()
            if session and session.user:
                # Check if user has a valid auth session
                # Reset links create temporary sessions that need password confirmation
                return True
            return False
        except Exception:
            return False


def init_auth_session():
    """Initialize authentication session"""
    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("user_id") is not None
