---
name: github-mcp
description: Use when the user asks to work with GitHub through MCP (repos, branches, commits, files, issues, pull requests, releases, tags, code search, Copilot jobs/reviews, and secret scanning). Includes explicit handling for missing tools and permission errors.
---

# GitHub MCP

This skill standardizes how to operate GitHub via MCP with predictable flows, explicit error handling, and no hallucinations about access.

## When To Use

Use this skill when the user asks for any GitHub operation, including:

- Repository discovery/listing
- Reading/writing files
- Branch, commit, release, or tag operations
- Issue/PR reading or updates
- Search across repositories/issues/PRs/code/users
- Copilot delegation/review workflows
- Secret scanning of supplied content

## Preconditions

Before executing multi-step work:

1. Confirm the GitHub MCP tools are available in the current session.
2. If a required tool is missing, stop and explain exactly which tool is unavailable.
3. If the tool exists but execution fails due auth/permission, report the exact failure and required remediation.

## Behavior Rules

- Always call `get_me` to identify the authenticated user before any operation when no profile name is explicitly provided by the user. `get_me` may be skipped only if the user explicitly passes the target profile or organization name they want to inspect.
- Never claim success without tool evidence.
- Never invent tool names not exposed by MCP.
- If a requested capability exists in this skill but is not exposed in the current session, say so explicitly.
- Prefer read operations first, then ask/confirm before destructive writes when needed.
- Keep user-facing explanations concise and actionable.

## Access Failure Handling

When a tool call fails, classify and respond like this:

- `tool not found` / unavailable in session:
  - Explain that the MCP session does not currently expose that tool.
  - Suggest reloading/restarting session or checking server configuration.

- `401 Unauthorized`:
  - Token invalid/expired or auth missing.
  - Ask user to re-authenticate or replace token.

- `403 Forbidden`:
  - Token authenticated but lacks scope/repo/org permission (or org SSO restrictions).
  - Tell user exactly what permission boundary blocked the action (repo, org, private/public).

- `404 Not Found`:
  - Could be wrong identifier or hidden private resource.
  - Ask user to confirm owner/repo/number/branch/path.

- `422 Unprocessable`:
  - Invalid parameters/state (e.g., SHA mismatch, branch conflict).
  - Provide corrective next input.

## Core Flows

### Flow: List user repositories (the one we used)

1. Call `get_me` to get the user name. 
2. Call `search_repositories` with query `user:<login>`.
3. If user asks for ordering by update date, sort by `updated_at desc` in result handling.
4. Return repository name, visibility, updated date, and URL.

### Flow: Read repository/file context

1. Resolve repo (`owner`, `repo`).
2. Call `list_branches` / `list_commits` if branch context needed.
3. Call `get_file_contents` for file or directory.
4. Summarize and include exact paths/refs used.

### Flow: Issue triage

1. Find target issue (`issue_read method=get`).
2. Read comments/labels if needed (`issue_read` variants).
3. Update or comment (`issue_write` / `add_issue_comment`).

### Flow: Pull request review pass

1. Read PR metadata (`pull_request_read method=get`).
2. Read files/diff/status/checks (`get_files`, `get_diff`, `get_check_runs`).
3. Add review comments (`add_comment_to_pending_review` or review APIs).
4. Optionally submit review (`pull_request_review_write`).

### Flow: Branch + file change + PR

1. Create branch (`create_branch`).
2. Modify content (`create_or_update_file` or `push_files`).
3. Open PR (`create_pull_request`).
4. Optionally request Copilot review (`request_copilot_review`).

### Flow: Copilot background implementation

1. Start job (`create_pull_request_with_copilot` or `assign_copilot_to_issue`).
2. Poll status (`get_copilot_job_status`).
3. Return PR link/result when finished.

## Full Tool Catalog (Directly From MCP Endpoint)

The following tools were collected directly from GitHub MCP endpoint (`tools/list`) during skill creation.
- `get_me`: ⭐ **One of the most critical tools in this catalog.** Returns the authenticated GitHub user's login, ID, and profile metadata. Must be called at the start of any operation where the target user is not explicitly specified — it is the source of truth for who is making the request. Without it, all user-scoped operations (listing repos, searching issues by author, etc.) risk targeting the wrong profile.
- `add_comment_to_pending_review`: Add review comment to the requester's latest pending pull request review. A pending review needs to already exist to call this (check with the user if not sure).
- `add_issue_comment`: Add a comment to a specific issue in a GitHub repository. Use this tool to add comments to pull requests as well (in this case pass pull request number as issue_number), but only if user is not asking specifically to add review comments.
- `add_reply_to_pull_request_comment`: Add a reply to an existing pull request comment. This creates a new comment that is linked as a reply to the specified comment.
- `assign_copilot_to_issue`: Assign Copilot to a specific issue in a GitHub repository.  This tool can help with the following outcomes: - a Pull Request created with source code changes to resolve the issue   More information can be found at: - https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent-to-work-on-tasks/about-assigning-tasks-to-copilot
- `create_branch`: Create a new branch in a GitHub repository
- `create_or_update_file`: Create or update a single file in a GitHub repository.  If updating, you should provide the SHA of the file you want to update. Use this tool to create or update a file in a GitHub repository remotely; do not use it for local file operations.  In order to obtain the SHA of original file version before updating, use the following git command: git rev-parse <branch>:<path to file>  SHA MUST be provided for existing file updates.
- `create_pull_request`: Create a new pull request in a GitHub repository.
- `create_pull_request_with_copilot`: Delegate a task to GitHub Copilot coding agent to perform in the background. The agent will create a pull request with the implementation. You should use this tool if the user asks to create a pull request to perform a specific task, or if the user asks Copilot to do something.
- `create_repository`: Create a new GitHub repository in your account or specified organization
- `delete_file`: Delete a file from a GitHub repository
- `fork_repository`: Fork a GitHub repository to your account or specified organization
- `get_commit`: Get details for a commit from a GitHub repository
- `get_copilot_job_status`: Get the status of a GitHub Copilot coding agent job. Use this to check if a previously submitted task has completed and to get the pull request URL once it's created. Provide the job ID (from create_pull_request_with_copilot) or pull request number (from assign_copilot_to_issue), or any pull request you want agent sessions for.
- `get_file_contents`: Get the contents of a file or directory from a GitHub repository
- `get_label`: Get a specific label from a repository.
- `get_latest_release`: Get the latest release in a GitHub repository
- `get_me`: Get details of the authenticated GitHub user. Use this when a request is about the user's own profile for GitHub. Or when information is missing to build other tool calls.
- `get_release_by_tag`: Get a specific release by its tag name in a GitHub repository
- `get_tag`: Get details about a specific git tag in a GitHub repository
- `get_team_members`: Get member usernames of a specific team in an organization. Limited to organizations accessible with current credentials
- `get_teams`: Get details of the teams the user is a member of. Limited to organizations accessible with current credentials
- `issue_read`: Get information about a specific issue in a GitHub repository.
- `issue_write`: Create a new or update an existing issue in a GitHub repository.
- `list_branches`: List branches in a GitHub repository
- `list_commits`: Get list of commits of a branch in a GitHub repository. Returns at least 30 results per page by default, but can return more if specified using the perPage parameter (up to 100).
- `list_issue_types`: List supported issue types for repository owner (organization).
- `list_issues`: List issues in a GitHub repository. For pagination, use the 'endCursor' from the previous response's 'pageInfo' in the 'after' parameter.
- `list_pull_requests`: List pull requests in a GitHub repository. If the user specifies an author, then DO NOT use this tool and use the search_pull_requests tool instead.
- `list_releases`: List releases in a GitHub repository
- `list_tags`: List git tags in a GitHub repository
- `merge_pull_request`: Merge a pull request in a GitHub repository.
- `pull_request_read`: Get information on a specific pull request in GitHub repository.
- `pull_request_review_write`: Create and/or submit, delete review of a pull request.  Available methods: - create: Create a new review of a pull request. If "event" parameter is provided, the review is submitted. If "event" is omitted, a pending review is created. - submit_pending: Submit an existing pending review of a pull request. This requires that a pending review exists for the current user on the specified pull request. The "body" and "event" parameters are used when submitting the review. - delete_pending: Delete an existing pending review of a pull request. This requires that a pending review exists for the current user on the specified pull request.
- `push_files`: Push multiple files to a GitHub repository in a single commit
- `request_copilot_review`: Request a GitHub Copilot code review for a pull request. Use this for automated feedback on pull requests, usually before requesting a human reviewer.
- `run_secret_scanning`: Scan files, content, or recent changes for secrets such as API keys, passwords, tokens, and credentials.  This tool is intended for targeted scans of specific files, snippets, or diffs provided directly as content. It accepts file contents or diffs and returns detected secrets with their locations and related secret scanning metadata. Content must not be empty. For full repository scanning, other mechanisms are available.  Caveats:  - Only files within the codebase should be scanned. Files outside of the codebase should not be sent. - Files listed in .gitignore should be skipped.
- `search_code`: Fast and precise code search across ALL GitHub repositories using GitHub's native search engine. Best for finding exact symbols, functions, classes, or specific code patterns.
- `search_issues`: Search for issues in GitHub repositories using issues search syntax already scoped to is:issue
- `search_pull_requests`: Search for pull requests in GitHub repositories using issues search syntax already scoped to is:pr
- `search_repositories`: Find GitHub repositories by name, description, readme, topics, or other metadata. Perfect for discovering projects, finding examples, or locating specific repositories across GitHub.
- `search_users`: Find GitHub users by username, real name, or other profile information. Useful for locating developers, contributors, or team members.
- `sub_issue_write`: Add a sub-issue to a parent issue in a GitHub repository.
- `update_pull_request`: Update an existing pull request in a GitHub repository.
- `update_pull_request_branch`: Update the branch of a pull request with the latest changes from the base branch.
