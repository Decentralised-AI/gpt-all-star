from gpt_all_star.core.agents.agents import Agents
from gpt_all_star.core.message import Message
from gpt_all_star.core.team import Team
from gpt_all_star.core.steps.step import Step
from gpt_all_star.core.agents.project_manager.implement_planning_prompt import (
    implement_planning_template,
)


class Development(Step):
    def __init__(
        self,
        agents: Agents,
        japanese_mode: bool,
        review_mode: bool,
        debug_mode: bool,
    ) -> None:
        super().__init__(agents, japanese_mode, review_mode, debug_mode)

    def run(self) -> None:
        team = Team(
            supervisor=self.agents.project_manager,
            members=[
                self.agents.engineer,
                self.agents.designer,
                self.agents.qa_engineer,
            ],
        )

        todo_list = self.agents.project_manager.plan_development(
            review_mode=self.review_mode
        )
        for i, task in enumerate(todo_list["plan"]):
            team.supervisor.state(
                f"""TODO {i + 1}: {task['todo']}
GOAL: {task['goal']}
---
"""
            )

            previous_finished_task_message = f"""The information given to you is as follows.
There are the specifications to build the application:
```
{team.supervisor.storages.docs["specifications.md"]}
```

There are the source codes generated so far:
```
{team.supervisor.current_source_code()}
```
"""
            message = Message.create_human_message(
                implement_planning_template.format(
                    todo_description=task["todo"],
                    finished_todo_message=previous_finished_task_message,
                    todo_goal=task["goal"],
                )
            )
            team.run([message])

        self.agents.engineer.create_source_code(review_mode=self.review_mode)
        self.agents.engineer.complete_source_code(review_mode=self.review_mode)
