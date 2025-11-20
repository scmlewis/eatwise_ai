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
                    
                    user_data = {
                        "user_id": user_id,
                        "email": email,
                        "full_name": ""
                    }
                else:
                    user_data = profile.data[0]
                
                # Fetch health profile and merge with user data
                health_profile = self.supabase.table("health_profiles").select("*").eq("user_id", user_id).execute()
                if health_profile.data:
                    user_data.update(health_profile.data[0])
                else:
                    # Auto-create a default health profile with sensible defaults if it doesn't exist
                    try:
                        default_profile = {
                            "user_id": user_id,
                            "full_name": user_data.get("full_name", ""),
                            "age_group": "26-35",  # Default age group
                            "gender": "Prefer not to say",
                            "timezone": "UTC",
                            "health_conditions": [],
                            "dietary_preferences": [],
                            "health_goal": "general_health"
                        }
                        self.supabase.table("health_profiles").insert(default_profile).execute()
                        user_data.update(default_profile)
                    except Exception as e:
                        # If auto-create fails, log it but continue
                        import sys
                        print(f"Warning: Could not auto-create health profile: {str(e)}", file=sys.stderr)
                        pass
                
                return True, "Login successful", user_data
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

