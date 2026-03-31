"""Tests for semantic layer"""

import pytest
import pandas as pd
from analytic_engine.semantic.registry import SemanticActionRegistry
from analytic_engine.semantic.actions import create_builtin_actions


class TestSemanticActionRegistry:
    """Test cases for SemanticActionRegistry"""

    def test_register_action(self, semantic_registry):
        """Test registering a new action"""

        def handler(param1: int) -> int:
            return param1 * 2

        semantic_registry.register("double", handler)
        actions = semantic_registry.list_actions()

        assert "double" in actions

    def test_execute_registered_action(self, semantic_registry):
        """Test executing a registered action"""

        def handler(x: int) -> int:
            return x + 10

        semantic_registry.register("add_ten", handler)
        result = semantic_registry.execute("add_ten", {"x": 5})

        assert result == 15

    def test_execute_unknown_action_raises_error(self, semantic_registry):
        """Test executing unknown action raises ValueError"""
        with pytest.raises(ValueError, match="Unknown action"):
            semantic_registry.execute("nonexistent", {})

    def test_list_actions(self, semantic_registry):
        """Test listing all registered actions"""
        semantic_registry.register("action1", lambda: None)
        semantic_registry.register("action2", lambda: None)

        actions = semantic_registry.list_actions()

        assert len(actions) == 2
        assert "action1" in actions
        assert "action2" in actions

    def test_get_action(self, semantic_registry):
        """Test retrieving an action handler"""
        handler = lambda x: x * 3
        semantic_registry.register("triple", handler)

        retrieved = semantic_registry.get_action("triple")

        assert retrieved is not None
        assert retrieved(5) == 15

    def test_get_nonexistent_action(self, semantic_registry):
        """Test retrieving nonexistent action returns None"""
        result = semantic_registry.get_action("missing")
        assert result is None


class TestBuiltinActions:
    """Test cases for built-in semantic actions"""

    def test_create_builtin_actions(self):
        """Test creating built-in actions"""
        actions = create_builtin_actions()

        assert "query_data" in actions
        assert "fetch_metrics" in actions
        assert "get_historical_data" in actions
        assert "get_aggregated" in actions

    def test_fetch_metrics_returns_dict(self):
        """Test fetch_metrics returns a dictionary"""
        actions = create_builtin_actions()
        result = actions["fetch_metrics"](metric_names=["revenue", "users"], timeframe="7d")

        assert isinstance(result, dict)
        assert "revenue" in result
        assert "users" in result

    def test_fetch_metrics_with_custom_timeframe(self):
        """Test fetch_metrics with different timeframes"""
        actions = create_builtin_actions()
        result = actions["fetch_metrics"](metric_names=["test"], timeframe="30d")

        assert result["test"] is None

    def test_query_data_without_accessor(self):
        """Test query_data returns empty DataFrame without accessor"""
        actions = create_builtin_actions()
        result = actions["query_data"](source="test", limit=10)

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_get_historical_data_returns_dataframe(self):
        """Test get_historical_data returns DataFrame"""
        actions = create_builtin_actions()
        result = actions["get_historical_data"](
            entity="sales", start_date="2024-01-01", end_date="2024-12-31"
        )

        assert isinstance(result, pd.DataFrame)

    def test_get_aggregated_returns_dataframe(self):
        """Test get_aggregated returns DataFrame"""
        actions = create_builtin_actions()
        result = actions["get_aggregated"](source="data", agg_func="mean", group_by=["category"])

        assert isinstance(result, pd.DataFrame)

    def test_get_aggregated_with_sum(self):
        """Test get_aggregated with sum aggregation"""
        actions = create_builtin_actions()
        result = actions["get_aggregated"](source="data", agg_func="sum")

        assert isinstance(result, pd.DataFrame)


class TestBuiltinActionsWithAccessor:
    """Test built-in actions with custom data accessor"""

    def test_query_data_with_accessor(self):
        """Test query_data uses custom accessor when provided"""
        mock_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        def mock_accessor(source, filters, columns, limit):
            return mock_df

        actions = create_builtin_actions(data_accessor=mock_accessor)
        result = actions["query_data"](source="test", limit=100)

        pd.testing.assert_frame_equal(result, mock_df)
