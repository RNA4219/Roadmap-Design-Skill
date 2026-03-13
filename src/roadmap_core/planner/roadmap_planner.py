"""Roadmap planner - core pipeline for generating roadmaps."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from roadmap_core.models.request import ConstraintSeverity, RoadmapRequest
from roadmap_core.models.response import (
    Confidence,
    Experiment,
    FailureItem,
    Fallback,
    Hypothesis,
    HypothesisStatus,
    NextAction,
    OpenQuestion,
    ProblemDefinition,
    Risk,
    RiskSeverity,
    RoadmapPhase,
    RoadmapResponse,
    RoadmapTask,
    RunMeta,
    RunStatus,
    SolutionOption,
    SuccessCriterion,
)
from roadmap_core.validators.request_validator import RequestValidator


class RoadmapPlanner:
    """Core planner for generating structured roadmaps from problem statements."""

    def __init__(self) -> None:
        self._validator = RequestValidator()
        self._planner_version = "1.1.0"

    def plan(self, request: RoadmapRequest) -> RoadmapResponse:
        run_id = request.run_id or (
            f"run_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        )
        now = datetime.now(timezone.utc)

        validation_errors = self._validator.validate(request)
        if validation_errors:
            return self._create_failure_response(
                run_id=run_id,
                now=now,
                problem_id=request.problem_statement.problem_id,
                title=request.problem_statement.title,
                errors=validation_errors,
                response_language=self._response_language(request),
            )

        broad_problem_check = self._check_broad_problem(request)
        if broad_problem_check:
            return self._create_partial_response(
                request=request,
                run_id=run_id,
                now=now,
                failures=broad_problem_check,
            )

        return self._generate_roadmap(request, run_id, now)

    def _generate_roadmap(
        self, request: RoadmapRequest, run_id: str, now: datetime
    ) -> RoadmapResponse:
        problem_definition = self._create_problem_definition(request)
        success_criteria = self._create_success_criteria(request)
        hypotheses = self._create_hypotheses(request)
        solution_options = self._create_solution_options(request, hypotheses)
        experiments = self._create_experiments(request, hypotheses)
        roadmap = self._create_roadmap_phases(request)
        risks = self._create_risks(request)
        fallbacks = self._create_fallbacks(request)
        next_actions = self._create_next_actions(roadmap)

        confidence = Confidence(
            score=self._confidence_score(request),
            reason=self._text(
                request,
                "入力された insight・constraint・asset の粒度が十分で、MVP の段階計画へ分解できるため。",
                "The provided insights, constraints, and assets are detailed enough to produce an MVP-oriented phased plan.",
            ),
        )

        return RoadmapResponse(
            schema_version="1.0.0",
            run=RunMeta(
                run_id=run_id,
                mode="roadmap",
                status=RunStatus.COMPLETED,
                created_at=now,
                updated_at=now,
                planner_version=self._planner_version,
                response_language=self._response_language(request),
            ),
            problem_definition=problem_definition,
            success_criteria=success_criteria,
            hypotheses=hypotheses,
            solution_options=solution_options,
            experiment_plan=experiments,
            roadmap=roadmap,
            risks=risks,
            fallback_options=fallbacks,
            next_actions=next_actions,
            open_questions=[],
            assumptions=request.assumptions or [],
            failures=[],
            confidence=confidence,
        )

    def _create_problem_definition(self, request: RoadmapRequest) -> ProblemDefinition:
        ps = request.problem_statement
        derived_from = [ins.insight_id for ins in request.insights[:3]]
        derived_from.extend(c.constraint_id for c in request.constraints[:2])
        if request.evidence_refs:
            derived_from.extend(ref.ref_id for ref in request.evidence_refs[:2])

        return ProblemDefinition(
            problem_id=ps.problem_id,
            title=ps.title,
            statement=ps.statement,
            scope=self._text(
                request,
                f"『{ps.title}』のMVP を対象に、{len(request.constraints)}件の制約と{len(request.available_assets)}件の資産を前提とした設計・検証計画を作る。",
                f"Create an MVP design and validation plan for '{ps.title}' under {len(request.constraints)} constraints and {len(request.available_assets)} available assets.",
            ),
            non_goals=self._non_goals(request),
            derived_from=derived_from,
        )

    def _create_success_criteria(self, request: RoadmapRequest) -> list[SuccessCriterion]:
        title = request.problem_statement.title
        desired = request.problem_statement.desired_outcome or title
        return [
            SuccessCriterion(
                criterion_id="sc_01",
                statement=self._text(request, f"{title} のMVPスコープとI/F契約が固定されている。", f"The MVP scope and interface contracts for {title} are fixed."),
                verification_method=self._text(request, "仕様レビューとschema validation", "Specification review and schema validation"),
                priority=1,
            ),
            SuccessCriterion(
                criterion_id="sc_02",
                statement=self._text(request, f"{desired} に直結する最小実装と検証手順が用意されている。", f"A minimum implementation and validation flow for {desired} is prepared."),
                verification_method=self._text(request, "プロトタイプ実行と受け入れ確認", "Prototype execution and acceptance check"),
                priority=2,
            ),
            SuccessCriterion(
                criterion_id="sc_03",
                statement=self._text(request, "次アクション・リスク・フォールバックが運用できる粒度で整理されている。", "Next actions, risks, and fallbacks are documented at an operationally actionable level."),
                verification_method=self._text(request, "Runbook と Evaluation のレビュー", "Runbook and evaluation review"),
                priority=3,
            ),
        ]

    def _create_hypotheses(self, request: RoadmapRequest) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []
        for i, insight in enumerate(request.insights[:3], start=1):
            hypotheses.append(
                Hypothesis(
                    hypothesis_id=f"hy_{i:02d}",
                    statement=self._text(request, f"『{insight.statement}』を設計判断へ反映すると、{request.problem_statement.title} の実装着手が早くなる。", f"Reflecting '{insight.statement}' in the design will accelerate delivery for {request.problem_statement.title}."),
                    why_this_might_work=self._text(request, "与えられた insight が制約と整合しており、初期フェーズで検証しやすいため。", "The insight aligns with the stated constraints and can be validated early in the plan."),
                    priority=i,
                    related_insight_ids=[insight.insight_id],
                    related_constraint_ids=[c.constraint_id for c in request.constraints[:2]],
                    status=HypothesisStatus.OPEN,
                )
            )

        while len(hypotheses) < 2:
            idx = len(hypotheses) + 1
            hypotheses.append(
                Hypothesis(
                    hypothesis_id=f"hy_{idx:02d}",
                    statement=self._text(request, f"{request.problem_statement.title} を薄いMVPに分割すれば、早期にフィードバックを得られる。", f"Splitting {request.problem_statement.title} into a thin-slice MVP will enable early feedback."),
                    why_this_might_work=self._text(request, "単一課題・同期MVPの制約と相性が良く、検証コストを抑えられるため。", "It fits the single-problem synchronous MVP boundary and reduces validation cost."),
                    priority=idx,
                    related_insight_ids=[request.insights[0].insight_id],
                    related_constraint_ids=[c.constraint_id for c in request.constraints[:2]],
                    status=HypothesisStatus.OPEN,
                )
            )
        return hypotheses

    def _create_solution_options(self, request: RoadmapRequest, hypotheses: list[Hypothesis]) -> list[SolutionOption]:
        primary_recommended = request.priority_hint in {None, "urgent", "high"}
        return [
            SolutionOption(
                option_id="op_01",
                title=self._text(request, "薄いMVPから始める", "Start with a thin-slice MVP"),
                summary=self._text(request, "コアユースケース、契約、評価ループを先に固定してから拡張する。", "Lock the core use case, contract, and evaluation loop first, then expand incrementally."),
                addresses_hypothesis_ids=[h.hypothesis_id for h in hypotheses[:2]],
                tradeoffs=self._localized_list(request, ["初期スコープの切り方が甘いと後で再設計が発生する", "周辺機能は後回しになる"], ["If the initial scope is weak, redesign may be needed later", "Peripheral features are deferred"]),
                recommended=primary_recommended,
            ),
            SolutionOption(
                option_id="op_02",
                title=self._text(request, "基盤を先に固める", "Stabilize the platform first"),
                summary=self._text(request, "評価基盤、監視、拡張性を先に整えてからユースケースを載せる。", "Build evaluation, observability, and extensibility foundations before layering use cases on top."),
                addresses_hypothesis_ids=[h.hypothesis_id for h in hypotheses],
                tradeoffs=self._localized_list(request, ["初期成果が見えにくい", "基盤過剰設計のリスクがある"], ["Early visible progress is smaller", "There is a risk of over-engineering the platform"]),
                recommended=not primary_recommended,
            ),
        ]

    def _create_experiments(self, request: RoadmapRequest, hypotheses: list[Hypothesis]) -> list[Experiment]:
        experiments: list[Experiment] = []
        for i, hypothesis in enumerate(hypotheses[:2], start=1):
            experiments.append(
                Experiment(
                    experiment_id=f"exp_{i:02d}",
                    title=self._text(request, f"仮説{i}の検証", f"Validate hypothesis {i}"),
                    goal=self._text(request, f"{hypothesis.hypothesis_id} が MVP 計画に有効か確認する。", f"Confirm whether {hypothesis.hypothesis_id} is useful for the MVP plan."),
                    verifies_hypothesis_ids=[hypothesis.hypothesis_id],
                    method=self._text(request, "小さなプロトタイプ、仕様レビュー、成功条件の照合を行う。", "Run a small prototype, review the design, and compare it against success criteria."),
                    success_condition=self._text(request, "主要な成功条件に対して実施可能な手順と成果物が定義される。", "Executable steps and deliverables are defined against the main success criteria."),
                    failure_signal=self._text(request, "必要な前提が不足し、次フェーズに進む判断ができない。", "Key assumptions remain unresolved and the next phase cannot be justified."),
                    depends_on=[] if i == 1 else ["exp_01"],
                    estimated_effort="0.5d" if i == 1 else "1d",
                )
            )
        return experiments

    def _create_roadmap_phases(self, request: RoadmapRequest) -> list[RoadmapPhase]:
        title = request.problem_statement.title
        phase_one_tasks = [
            RoadmapTask(task_id="tk_01", title=self._text(request, "対象ユーザーとゴールを固定する", "Lock target users and goals"), description=self._text(request, f"{title} の一次利用者、入力、期待結果を1ページにまとめる。", f"Summarize primary users, inputs, and expected outcomes for {title} in one page."), deliverable="problem brief", depends_on=[]),
            RoadmapTask(task_id="tk_02", title=self._text(request, "契約と評価指標を定義する", "Define contracts and evaluation metrics"), description=self._text(request, "request / response / validation-result のI/Fと受け入れ条件を固定する。", "Fix the request / response / validation-result interfaces and acceptance criteria."), deliverable="schema set and evaluation checklist", depends_on=["tk_01"]),
            RoadmapTask(task_id="tk_03", title=self._text(request, "最小エージェントループを設計する", "Design the minimum agent loop"), description=self._text(request, "planner、tool call、memory、fallback の最小ループを図と文章で整理する。", "Describe the minimum loop across planner, tool calls, memory, and fallback behavior in text and diagrams."), deliverable="MVP architecture draft", depends_on=["tk_02"]),
        ]
        phase_two_tasks = [
            RoadmapTask(task_id="tk_04", title=self._text(request, "コアフローを実装する", "Implement the core flow"), description=self._text(request, "入力正規化、計画生成、validate を一貫したCLI/HTTP/MCPで動かす。", "Make normalization, planning, and validation work consistently across CLI/HTTP/MCP."), deliverable="working prototype", depends_on=["tk_03"]),
            RoadmapTask(task_id="tk_05", title=self._text(request, "ガードレールと失敗系を実装する", "Implement guardrails and failure handling"), description=self._text(request, "invalid input、broad problem、fallback の扱いを明確にする。", "Clarify the handling of invalid input, broad problems, and fallback behavior."), deliverable="error and fallback behaviors", depends_on=["tk_04"]),
            RoadmapTask(task_id="tk_06", title=self._text(request, "代表シナリオで評価する", "Evaluate with representative scenarios"), description=self._text(request, "AIエージェント構築のサンプル要求で、出力の妥当性と次アクションの粒度を確認する。", "Use representative AI agent planning scenarios to check output quality and next-action granularity."), deliverable="evaluation report", depends_on=["tk_05"]),
        ]
        phase_three_tasks = [
            RoadmapTask(task_id="tk_07", title=self._text(request, "運用文書とサンプルを整理する", "Organize operational docs and examples"), description=self._text(request, "README、Runbook、サンプル入出力、Task Seed を実装と整合させる。", "Align README, Runbook, sample inputs/outputs, and Task Seed templates with the implementation."), deliverable="updated docs and examples", depends_on=["tk_06"]),
            RoadmapTask(task_id="tk_08", title=self._text(request, "次の拡張候補を決める", "Choose the next extension"), description=self._text(request, "memory、tool routing、observability のどれを次に進めるか優先順位を付ける。", "Prioritize the next extension across memory, tool routing, and observability."), deliverable="prioritized backlog", depends_on=["tk_07"]),
        ]
        return [
            RoadmapPhase(phase_id="ph_01", order=1, title=self._text(request, "課題定義と契約固定", "Problem framing and contract freeze"), goal=self._text(request, f"{title} のMVP境界と成功条件を固定する。", f"Freeze the MVP boundary and success criteria for {title}."), exit_criteria=self._localized_list(request, ["problem brief が合意されている", "schema と評価条件が揃っている"], ["The problem brief is agreed upon", "Schemas and evaluation criteria are aligned"]), tasks=phase_one_tasks),
            RoadmapPhase(phase_id="ph_02", order=2, title=self._text(request, "コア実装と検証", "Core implementation and validation"), goal=self._text(request, "最小エージェントループを実装し、主要仮説を検証する。", "Implement the minimum agent loop and validate the main hypotheses."), exit_criteria=self._localized_list(request, ["主要シナリオで動作する", "failure / fallback の扱いが確認できる"], ["The primary scenario works", "Failure and fallback behavior are verified"]), tasks=phase_two_tasks),
            RoadmapPhase(phase_id="ph_03", order=3, title=self._text(request, "運用整理と拡張準備", "Operational hardening and next-step prep"), goal=self._text(request, "運用文書、サンプル、次フェーズ候補を整理する。", "Organize documentation, examples, and next-phase options."), exit_criteria=self._localized_list(request, ["再実行できるサンプルが残っている", "次の優先拡張が決まっている"], ["A reproducible sample is stored", "The next prioritized extension is chosen"]), tasks=phase_three_tasks),
        ]

    def _create_risks(self, request: RoadmapRequest) -> list[Risk]:
        risks: list[Risk] = []
        for index, constraint in enumerate(request.constraints[:2], start=1):
            severity = RiskSeverity.HIGH if constraint.severity == ConstraintSeverity.HARD else RiskSeverity.MEDIUM
            risks.append(Risk(risk_id=f"rk_{index:02d}", statement=self._text(request, f"制約『{constraint.statement}』が実装順を圧迫する可能性がある。", f"Constraint '{constraint.statement}' may pressure the delivery sequence."), severity=severity, mitigation=self._text(request, "早い段階でスコープを固定し、受け入れ条件を先に確認する。", "Freeze scope early and verify acceptance criteria before building too much.")))
        if request.known_failures:
            for offset, failure in enumerate(request.known_failures[:1], start=len(risks) + 1):
                risks.append(Risk(risk_id=f"rk_{offset:02d}", statement=self._text(request, f"既知失敗『{failure.statement}』が再発する恐れがある。", f"Known failure '{failure.statement}' may recur."), severity=RiskSeverity.HIGH, mitigation=self._text(request, "failure の再発条件をテストとガードレールに落とし込む。", "Convert the failure condition into tests and guardrails.")))
        return risks or [Risk(risk_id="rk_01", statement=self._text(request, "要件が途中で膨らみ、MVPの焦点がぼやける恐れがある。", "Requirements may expand mid-flight and blur the MVP focus."), severity=RiskSeverity.MEDIUM, mitigation=self._text(request, "phase ごとの exit criteria を使って段階的に判断する。", "Use phase exit criteria to keep decisions staged and explicit."))]

    def _create_fallbacks(self, request: RoadmapRequest) -> list[Fallback]:
        if request.known_failures:
            return [Fallback(fallback_id="fb_01", trigger=self._text(request, "主要仮説の検証が失敗したとき", "When the primary hypothesis fails validation"), statement=self._text(request, "薄いMVPへ戻し、要件を削って再計画する。", "Return to a thinner MVP slice, reduce scope, and re-plan."), tradeoff=self._text(request, "短期的な機能量は減るが、再現性と学習速度は上がる。", "Short-term feature scope shrinks, but reproducibility and learning speed improve."))]
        return [Fallback(fallback_id="fb_01", trigger=self._text(request, "初回実装が想定より重いとき", "When the first implementation is heavier than expected"), statement=self._text(request, "CLI 単体に絞って validate と run を先に完成させる。", "Narrow scope to CLI only and finish validate and run first."), tradeoff=self._text(request, "外部I/Fの検証は後ろ倒しになる。", "External interface validation is deferred."))]

    def _create_next_actions(self, roadmap: list[RoadmapPhase]) -> list[NextAction]:
        actions: list[NextAction] = []
        if roadmap and roadmap[0].tasks:
            for i, task in enumerate(roadmap[0].tasks[:3], start=1):
                depends_on = [] if i == 1 else [f"na_{i - 1:02d}"]
                actions.append(
                    NextAction(
                        action_id=f"na_{i:02d}",
                        title=task.title,
                        description=task.description,
                        deliverable=task.deliverable,
                        depends_on=depends_on,
                    )
                )
        return actions

    def _check_broad_problem(self, request: RoadmapRequest) -> list[FailureItem] | None:
        statement = request.problem_statement.statement
        if len(statement.strip()) < 20:
            return [FailureItem(failure_id="fl_01", type="input_gap", summary=self._text(request, "課題文が短すぎて計画を安定して作れない。", "The problem statement is too short to create a stable plan."), recoverable=True)]
        return None

    def _create_failure_response(self, run_id: str, now: datetime, problem_id: str, title: str, errors: list[str], response_language: str) -> RoadmapResponse:
        return RoadmapResponse(
            schema_version="1.0.0",
            run=RunMeta(run_id=run_id, mode="roadmap", status=RunStatus.FAILED, created_at=now, updated_at=now, planner_version=self._planner_version, response_language=response_language),
            problem_definition=ProblemDefinition(problem_id=problem_id, title=title, statement=("バリデーションに失敗した。" if response_language.startswith("ja") else "Validation failed"), scope=("該当なし" if response_language.startswith("ja") else "N/A"), non_goals=[], derived_from=[]),
            success_criteria=[], hypotheses=[], solution_options=[], experiment_plan=[], roadmap=[], risks=[], fallback_options=[], next_actions=[], open_questions=[], assumptions=[],
            failures=[FailureItem(failure_id="fl_01", type="input_gap", summary=(errors[0] if errors else ("バリデーションに失敗した。" if response_language.startswith("ja") else "Validation failed")), recoverable=True)],
            confidence=Confidence(score=0.0, reason=("入力が不足しているため計画を生成できない。" if response_language.startswith("ja") else "Request validation failed.")),
        )

    def _create_partial_response(self, request: RoadmapRequest, run_id: str, now: datetime, failures: list[FailureItem]) -> RoadmapResponse:
        ps = request.problem_statement
        return RoadmapResponse(
            schema_version="1.0.0",
            run=RunMeta(run_id=run_id, mode="roadmap", status=RunStatus.PARTIAL, created_at=now, updated_at=now, planner_version=self._planner_version, response_language=self._response_language(request)),
            problem_definition=ProblemDefinition(problem_id=ps.problem_id, title=ps.title, statement=ps.statement, scope=self._text(request, "課題範囲が広すぎるため、完全なロードマップではなく再定義が必要。", "The scope is too broad, so the problem must be reframed before a full roadmap can be produced."), non_goals=[], derived_from=[]),
            success_criteria=[], hypotheses=[], solution_options=[], experiment_plan=[], roadmap=[], risks=[], fallback_options=[], next_actions=[],
            open_questions=[OpenQuestion(question_id="oq_01", statement=self._text(request, "対象ユーザー、入力、期待成果をもう少し具体化できるか。", "Can the target users, inputs, and desired outcomes be made more concrete?"), blocking=True, affects=["roadmap generation"])],
            assumptions=[], failures=failures,
            confidence=Confidence(score=0.3, reason=self._text(request, "入力のスコープが広く、段階計画へ落とし切れていない。", "The input scope is too broad to decompose into a phased roadmap.")),
        )

    def _confidence_score(self, request: RoadmapRequest) -> float:
        score = 0.62
        score += min(len(request.insights), 3) * 0.05
        score += min(len(request.available_assets), 3) * 0.03
        hard_constraints = sum(1 for c in request.constraints if c.severity == ConstraintSeverity.HARD)
        score -= min(hard_constraints, 3) * 0.03
        return max(0.45, min(score, 0.85))

    def _non_goals(self, request: RoadmapRequest) -> list[str]:
        return self._localized_list(request, ["長期run storeの設計", "マルチテナント認証", "本番運用の全面自動化"], ["Long-term run store design", "Multi-tenant authentication", "Full production automation"])

    def _response_language(self, request: RoadmapRequest) -> str:
        if request.response_language:
            return request.response_language
        return "ja"

    def _is_japanese(self, request: RoadmapRequest) -> bool:
        return self._response_language(request).lower().startswith("ja")

    def _text(self, request: RoadmapRequest, ja: str, en: str) -> str:
        return ja if self._is_japanese(request) else en

    def _localized_list(self, request: RoadmapRequest, ja: list[str], en: list[str]) -> list[str]:
        return ja if self._is_japanese(request) else en
