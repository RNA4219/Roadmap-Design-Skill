"""Prompt templates for LLM-based roadmap generation."""

from __future__ import annotations

import json
from typing import Any


class PromptTemplates:
    """Prompt templates for roadmap generation."""

    @staticmethod
    def get_system_prompt(language: str = "en") -> str:
        """Get system prompt for roadmap generation.

        Args:
            language: Response language (en, ja, etc.).

        Returns:
            System prompt string.
        """
        if language == "ja":
            return """あなたはロードマップ設計の専門家です。
与えられた課題、洞察、制約、利用可能な資産に基づいて、実装可能なロードマップを生成してください。

出力は必ず有効なJSON形式で、以下の構造に従ってください：
- problem_definition: 再定義された課題
- success_criteria: 成功基準のリスト
- hypotheses: 検証すべき仮説（2つ以上推奨）
- solution_options: 解決策の選択肢
- experiment_plan: 実験計画
- roadmap: フェーズごとのロードマップ（各フェーズにタスクを含む）
- risks: リスク評価
- fallback_options: フォールバック計画
- next_actions: 次のアクション（構造化されたオブジェクト）
- open_questions: 未解決の質問
- assumptions: 前提条件
- failures: 失敗項目（ある場合）
- confidence: 信頼度スコア（0-1）と理由

すべてのIDは適切なプレフィックスを使用してください：
- 問題: pb_
- 洞察: in_
- 制約: co_
- 資産: as_
- 仮説: hy_
- 成功基準: sc_
- 解決策: op_
- 実験: exp_
- フェーズ: ph_
- タスク: tk_
- リスク: rk_
- フォールバック: fb_
- 次アクション: na_
- 質問: oq_
- 失敗: fl_"""

        return """You are an expert roadmap designer.
Based on the provided problem, insights, constraints, and available assets, generate an implementation-ready roadmap.

Output must be valid JSON following this structure:
- problem_definition: Redefined problem statement
- success_criteria: List of success criteria
- hypotheses: Hypotheses to validate (2+ recommended)
- solution_options: Solution alternatives
- experiment_plan: Experiment plan
- roadmap: Phased roadmap with tasks in each phase
- risks: Risk assessment
- fallback_options: Fallback plans
- next_actions: Structured next action objects
- open_questions: Open questions
- assumptions: Assumptions made
- failures: Failure items (if any)
- confidence: Confidence score (0-1) with reason

Use appropriate ID prefixes:
- Problem: pb_
- Insight: in_
- Constraint: co_
- Asset: as_
- Hypothesis: hy_
- Success criterion: sc_
- Solution option: op_
- Experiment: exp_
- Phase: ph_
- Task: tk_
- Risk: rk_
- Fallback: fb_
- Next action: na_
- Question: oq_
- Failure: fl_"""

    @staticmethod
    def get_enhancement_prompt(
        request: dict[str, Any],
        baseline: dict[str, Any],
    ) -> str:
        """Get prompt for enhancing baseline roadmap.

        Args:
            request: Original request.
            baseline: Baseline roadmap from deterministic planner.

        Returns:
            Enhancement prompt string.
        """
        # Simplified prompt to avoid timeout
        problem = request.get("problem_statement", {})
        insights = request.get("insights", [])[:2]  # Limit to 2 insights
        constraints = request.get("constraints", [])[:2]  # Limit to 2 constraints

        return f"""Enhance this roadmap for: {problem.get('title', 'Unknown')}

Problem: {problem.get('statement', '')[:200]}

Key Insights: {[i.get('statement', '')[:50] for i in insights]}
Constraints: {[c.get('statement', '')[:50] for c in constraints]}

Baseline Roadmap:
{json.dumps(baseline.get('roadmap', []), ensure_ascii=False)}

Return enhanced JSON with:
1. Better hypotheses (2-3)
2. Specific experiments
3. Realistic risks
4. Actionable next_actions

Output only valid JSON matching the schema."""