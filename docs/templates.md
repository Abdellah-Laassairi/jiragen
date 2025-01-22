# Templates

JiraGen uses templates to structure generated JIRA issues consistently. This guide covers template usage, customization, and best practices.

## Default Templates

JiraGen comes with several built-in templates:

### Standard Issue Template (`default.md`)
```markdown
# {title}

## Description
{description}

## Acceptance Criteria
- [ ] {criteria_1}
- [ ] {criteria_2}
- [ ] {criteria_3}

## Technical Details
{technical_details}

## Implementation Notes
- {note_1}
- {note_2}
```

### Bug Report Template (`bug.md`)
```markdown
# {title}

## Description
{description}

## Steps to Reproduce
1. {step_1}
2. {step_2}
3. {step_3}

## Expected Behavior
{expected}

## Actual Behavior
{actual}

## Technical Details
- Environment: {environment}
- Version: {version}
- Browser/Device: {browser}

## Possible Solution
{solution}
```

### Feature Request Template (`feature.md`)
```markdown
# {title}

## Description
{description}

## User Story
As a {user_type}
I want to {action}
So that {benefit}

## Acceptance Criteria
- [ ] {criteria_1}
- [ ] {criteria_2}
- [ ] {criteria_3}

## Technical Approach
{technical_approach}

## Dependencies
- {dependency_1}
- {dependency_2}
```

## Custom Templates

### Creating Templates

1. Create a new markdown file in your templates directory:
   - Unix-like: `~/.config/jiragen/templates/`
   - Windows: `%APPDATA%\jiragen\templates/`

2. Use template variables:
   - `{title}`: Issue title
   - `{description}`: AI-generated description
   - `{technical_details}`: Technical implementation details
   - Custom variables: Define any variable with `{variable_name}`

### Template Variables

Variables are replaced with AI-generated content or user-provided values:

```markdown
# {title}

## Overview
{description}

## Custom Section
{my_custom_variable}
```

### Using Custom Templates

```bash
# Use a specific template
jiragen generate "Add dark mode" --template feature.md

# Use a custom template
jiragen generate "Fix memory leak" --template custom/bug_report.md
```

## Template Best Practices

1. **Structure**:
   - Use clear headings
   - Include acceptance criteria
   - Add technical details section
   - Consider adding checklists

2. **Variables**:
   - Use descriptive names
   - Document custom variables
   - Keep optional sections modular

3. **Formatting**:
   - Use markdown for consistency
   - Include code block templates where needed
   - Consider JIRA markup compatibility

4. **Sections to Consider**:
   - Description/Overview
   - Acceptance Criteria
   - Technical Details
   - Dependencies
   - Testing Requirements
   - Documentation Needs
