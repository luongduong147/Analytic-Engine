"""Tree of Thought reasoning implementation"""

from typing import List, Optional, Dict, Any
from dataclasses import field
from ..types import AnalysisRequest, ThoughtStep, ReasoningMode


class ThoughtTreeNode:
    """Node in the thought tree"""

    def __init__(self, step: ThoughtStep, depth: int = 0):
        self.step = step
        self.depth = depth
        self.children: List["ThoughtTreeNode"] = []
        self.score: float = 0.0

    def add_child(self, child: "ThoughtTreeNode") -> None:
        self.children.append(child)

    def get_best_child(self) -> Optional["ThoughtTreeNode"]:
        if not self.children:
            return None
        return max(self.children, key=lambda n: n.score)

    def get_all_paths(self) -> List[List[ThoughtStep]]:
        """Get all possible paths from this node"""
        if not self.children:
            return [[self.step]]

        paths = []
        for child in self.children:
            for path in child.get_all_paths():
                paths.append([self.step] + path)
        return paths


class TreeOfThought:
    """Tree of Thought reasoning implementation"""

    def __init__(self, cot_reasoner: Any, max_branches: int = 3, max_depth: int = 5):
        self.cot = cot_reasoner
        self.max_branches = max_branches
        self.max_depth = max_depth

    def reason(self, request: AnalysisRequest) -> List[ThoughtStep]:
        """Execute tree of thought reasoning"""
        root = ThoughtTreeNode(
            ThoughtStep(step_number=0, thought=request.objective, action="start", result=None)
        )

        self._expand_tree(root, request, current_depth=0)

        best_path = self._find_best_path(root)
        return best_path

    def _expand_tree(
        self, node: ThoughtTreeNode, request: AnalysisRequest, current_depth: int
    ) -> None:
        """Expand tree with branches"""
        if current_depth >= self.max_depth:
            return

        branches = self._generate_branches(node.step, current_depth)

        for branch_action in branches[: self.max_branches]:
            child_step = ThoughtStep(
                step_number=current_depth + 1,
                thought=branch_action["thought"],
                action=branch_action["action"],
                result=branch_action.get("result"),
            )
            child_node = ThoughtTreeNode(child_step, current_depth + 1)
            child_node.score = branch_action.get("score", 0.5)
            node.add_child(child_node)

            self._expand_tree(child_node, request, current_depth + 1)

    def _generate_branches(self, current_step: ThoughtStep, depth: int) -> List[Dict[str, Any]]:
        """Generate multiple branches from current step"""
        actions = ["query_data", "fetch_metrics", "get_aggregated", "analyze"]
        branches = []

        for action in actions[: self.max_branches]:
            branches.append(
                {
                    "thought": f"Explore {action} at depth {depth}",
                    "action": action,
                    "score": 1.0 / (depth + 1),
                }
            )

        return branches

    def _find_best_path(self, root: ThoughtTreeNode) -> List[ThoughtStep]:
        """Find the best scoring path"""
        paths = root.get_all_paths()
        if not paths:
            return [root.step]

        best = max(paths, key=lambda p: sum(s.confidence for s in p))
        return best
