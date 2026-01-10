"""
Pytest configuration and shared fixtures for EatWise tests.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date, timedelta
import json


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def test_user_id():
    """Generate a test user ID"""
    return "test-user-12345-abcde"


@pytest.fixture
def test_user_email():
    """Test user email"""
    return "testuser@example.com"


@pytest.fixture
def test_user_profile():
    """Sample user health profile"""
    return {
        "user_id": "test-user-12345-abcde",
        "full_name": "Test User",
        "age_group": "26-35",
        "gender": "Female",
        "health_goal": "weight_loss",
        "health_conditions": ["diabetes"],
        "dietary_preferences": ["vegetarian"],
        "height_cm": 165,
        "weight_kg": 70,
        "water_goal_glasses": 8,
        "timezone": "America/New_York"
    }


@pytest.fixture
def test_meal_data():
    """Sample meal data"""
    return {
        "user_id": "test-user-12345-abcde",
        "meal_name": "Grilled Chicken Salad",
        "meal_type": "lunch",
        "calories": 450,
        "protein": 35.0,
        "carbs": 20.0,
        "fat": 25.0,
        "sodium": 600,
        "sugar": 5.0,
        "fiber": 8.0,
        "logged_at": datetime.now().isoformat(),
        "notes": "With olive oil dressing"
    }


@pytest.fixture
def test_nutrition_data():
    """Sample nutrition analysis result"""
    return {
        "calories": 450,
        "protein": 35.0,
        "carbs": 20.0,
        "fat": 25.0,
        "sodium": 600,
        "sugar": 5.0,
        "fiber": 8.0
    }


@pytest.fixture
def test_daily_targets():
    """Sample daily nutrition targets"""
    return {
        "calories": 2000,
        "protein": 50,
        "carbs": 300,
        "fat": 65,
        "sodium": 2300,
        "sugar": 50,
        "fiber": 25
    }


@pytest.fixture
def test_meals_list(test_meal_data):
    """List of meals for streak/history testing"""
    base_date = datetime.now()
    meals = []
    for i in range(7):
        meal = test_meal_data.copy()
        meal["logged_at"] = (base_date - timedelta(days=i)).isoformat()
        meal["meal_name"] = f"Meal Day {i}"
        meals.append(meal)
    return meals


# ============================================================================
# Mock Fixtures - Supabase
# ============================================================================

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for database tests"""
    mock_client = MagicMock()
    
    # Mock table operations
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Chain methods (select, insert, update, delete, eq, etc.)
    mock_table.select.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.range.return_value = mock_table
    
    # Default execute response
    mock_response = MagicMock()
    mock_response.data = []
    mock_table.execute.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_supabase_auth():
    """Mock Supabase auth for authentication tests"""
    mock_auth = MagicMock()
    
    # Mock successful sign up
    mock_user = MagicMock()
    mock_user.id = "test-user-12345-abcde"
    mock_user.email = "testuser@example.com"
    
    mock_response = MagicMock()
    mock_response.user = mock_user
    
    mock_auth.sign_up.return_value = mock_response
    mock_auth.sign_in_with_password.return_value = mock_response
    mock_auth.sign_out.return_value = None
    
    return mock_auth


# ============================================================================
# Mock Fixtures - Azure OpenAI
# ============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock Azure OpenAI client for AI tests"""
    mock_client = MagicMock()
    
    # Mock chat completion response
    mock_message = MagicMock()
    mock_message.content = json.dumps({
        "calories": 450,
        "protein": 35.0,
        "carbs": 20.0,
        "fat": 25.0,
        "sodium": 600,
        "sugar": 5.0,
        "fiber": 8.0
    })
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = MagicMock(total_tokens=100)
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_openai_rate_limit_error():
    """Mock rate limit error from OpenAI"""
    from openai import RateLimitError
    
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"retry-after": "60"}
    
    return RateLimitError(
        message="Rate limit exceeded",
        response=mock_response,
        body={"error": {"message": "Rate limit exceeded"}}
    )


# ============================================================================
# Mock Fixtures - Streamlit
# ============================================================================

class MockSessionState:
    """A mock session_state that allows attribute access like streamlit's"""
    def __init__(self):
        self._state = {
            'user_id': "test-user-12345-abcde",
            'user_email': "testuser@example.com",
            'user_profile': None,
            'current_page': "Dashboard",
            'pagination_page': 0,
        }
    
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return self._state.get(name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self._state[name] = value
    
    def __contains__(self, key):
        return key in self._state
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __setitem__(self, key, value):
        self._state[key] = value


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit module with proper session state"""
    mock_st = MagicMock()
    mock_st.session_state = MockSessionState()
    mock_st.error = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.success = MagicMock()
    mock_st.info = MagicMock()
    return mock_st


@pytest.fixture
def mock_st_error():
    """Mock st.error for testing error displays"""
    with patch('streamlit.error') as mock_error:
        yield mock_error


@pytest.fixture
def mock_st_success():
    """Mock st.success for testing success messages"""
    with patch('streamlit.success') as mock_success:
        yield mock_success


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_db_response(data):
    """Create a mock Supabase execute response with data"""
    mock_response = MagicMock()
    mock_response.data = data if isinstance(data, list) else [data]
    return mock_response


def create_mock_ai_response(content):
    """Create a mock OpenAI chat completion response"""
    mock_message = MagicMock()
    mock_message.content = content if isinstance(content, str) else json.dumps(content)
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = MagicMock(total_tokens=100)
    
    return mock_response


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
