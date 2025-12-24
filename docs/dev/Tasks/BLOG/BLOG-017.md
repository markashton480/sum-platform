# BLOG.017: Sage & Stone Deployment and Validation

**Phase:** 5 - Testing + Deployment  
**Priority:** P1  
**Estimated Hours:** 7h  
**Dependencies:** BLOG.016

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-017-deployment
```

## Objective

Deploy Blog v1 + Dynamic Forms v1 to Sage & Stone demo site, create sample content, and validate all Definition of Done criteria. Run final Lighthouse audit and verify production readiness.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:591-605`
- Deployment Runbook: `docs/ops-pack/deploy-runbook.md`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Deployment Steps

1. **Merge to Main**
   - Ensure all PRs merged to develop
   - Create release PR: develop → main
   - Run full CI checks
   - Review and merge

2. **Deploy to Sage & Stone**
   - Follow deployment runbook
   - Run migrations
   - Collect static files
   - Restart services

3. **Create Sample FormDefinitions**
   - Newsletter signup (email only)
   - Contact/callback request (name, email, phone, message)
   - Quote request (name, email, company, service interest, message)

4. **Create Sample Blog Content**
   - At least 5 blog posts
   - Multiple categories (3+)
   - Each post with DynamicFormBlock CTA
   - Vary featured images
   - Mix of short and long posts

5. **Validation Testing**
   - Test all form submissions
   - Verify email notifications
   - Test webhooks (if configured)
   - Verify pagination
   - Test category filtering
   - Test responsive design

6. **Performance Validation**
   - Run Lighthouse audits
   - Verify targets: ≥90 all metrics
   - Check CSS bundle size
   - Measure form submission latency

## Implementation Tasks

### Pre-Deployment

- [ ] Ensure all BLOG.001-016 PRs merged to develop
- [ ] Create release PR: develop → main
- [ ] Run full test suite on main branch
- [ ] Review all code changes
- [ ] Update CHANGELOG (if applicable)

### Deployment

- [ ] Follow deployment runbook steps
- [ ] Backup database before deployment
- [ ] Deploy to Sage & Stone staging (if available)
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Restart Gunicorn and Celery services
- [ ] Verify deployment successful (site loads)

### Content Creation

- [ ] Create 3 categories:
  - "Company News"
  - "Industry Insights"
  - "Case Studies"

- [ ] Create 3 FormDefinitions:
  - **Newsletter Signup**
    - Fields: email
    - Success message: "Thanks for subscribing!"
    - Email notification enabled
  
  - **Contact Request**
    - Fields: name, email, phone, message (textarea)
    - Success message: "We'll get back to you soon!"
    - Email notification + auto-reply enabled
  
  - **Quote Request**
    - Fields: name, email, company, service (select), message
    - Success message: "Quote request received!"
    - Email notification + webhook enabled

- [ ] Create BlogIndexPage at `/blog/`
  - Intro text describing blog

- [ ] Create 5+ BlogPostPages:
  - Mix of categories
  - Varied publish dates
  - Different reading times (short, medium, long)
  - Each with 1-2 DynamicFormBlock instances
  - Featured images for all
  - Author names (optional)

### Validation

- [ ] Test form submissions:
  - Submit each FormDefinition type
  - Verify Leads created in admin
  - Check email notifications received
  - Test webhook delivery (if configured)

- [ ] Test blog functionality:
  - Navigate to /blog/
  - Verify posts display
  - Test pagination (if 10+ posts)
  - Test category filter
  - Click into individual posts
  - Verify forms render in posts

- [ ] Test responsive design:
  - Mobile (375px, 414px)
  - Tablet (768px, 1024px)
  - Desktop (1440px+)

- [ ] Run Lighthouse audits:
  - Blog index: `lighthouse https://sageandstone.example.com/blog/ --view`
  - Blog post: `lighthouse https://sageandstone.example.com/blog/sample-post/ --view`
  - Target: ≥90 (Performance, Accessibility, Best Practices, SEO)

- [ ] Verify Definition of Done:
  - Dynamic Forms:
    - [ ] FormDefinition creatable as snippet
    - [ ] All field types work and validate
    - [ ] DynamicFormBlock selectable in pages
    - [ ] Submissions save to Lead model
    - [ ] Email notifications send
    - [ ] Webhooks fire correctly
    - [ ] Clone/duplicate form works
    - [ ] Active toggle works
    - [ ] Multiple forms on same page tested
    - [ ] Backwards compatible with static forms
  
  - Blog:
    - [ ] Blog pages creatable in admin
    - [ ] Listing pagination works
    - [ ] Category filtering works
    - [ ] Featured images display correctly
    - [ ] Reading time displays correctly
    - [ ] SEO tags render correctly
    - [ ] Lighthouse targets met (≥90)
    - [ ] Templates match Sage & Stone UI
  
  - Integration:
    - [ ] Deployed to Sage & Stone
    - [ ] At least 3 distinct form placements
    - [ ] Blog uses DynamicFormBlock for CTAs
    - [ ] Used for real blog posts

## Acceptance Criteria

- [ ] All code merged to main branch
- [ ] Deployed to Sage & Stone successfully
- [ ] Migrations run without errors
- [ ] Static files collected and serving
- [ ] 3+ FormDefinitions created
- [ ] 3+ categories created
- [ ] 5+ blog posts created with forms
- [ ] All form submissions work
- [ ] Email notifications delivered
- [ ] Webhooks fire (if configured)
- [ ] Blog pagination works
- [ ] Category filtering works
- [ ] Lighthouse score ≥90 (all metrics)
- [ ] Responsive on all screen sizes
- [ ] All Definition of Done items verified
- [ ] No critical bugs detected

## Testing Commands

```bash
# Pre-deployment checks
make test
make lint

# Post-deployment verification
curl -I https://sageandstone.example.com/blog/
curl -I https://sageandstone.example.com/admin/

# Lighthouse audits
lighthouse https://sageandstone.example.com/blog/ --view
lighthouse https://sageandstone.example.com/blog/sample-post/ --view

# Test form submission
curl -X POST https://sageandstone.example.com/forms/submit/ \
  -d "form_definition_id=1&email=test@example.com"

# Monitor logs
ssh sageandstone "tail -f /var/log/sum-site/gunicorn.log"
ssh sageandstone "tail -f /var/log/sum-site/celery.log"
```

## Post-Implementation

**Merge and tag release:**
```bash
# After successful deployment
git checkout main
git tag -a v1.0.0-blog-forms -m "Release: Blog v1 + Dynamic Forms v1"
git push origin v1.0.0-blog-forms

# Create GitHub release
gh release create v1.0.0-blog-forms \
  --title "Blog v1 + Dynamic Forms v1" \
  --notes "## Features

### Blog v1
- BlogIndexPage with pagination and category filtering
- BlogPostPage with reading time and featured images
- Category taxonomy
- SEO optimized with structured data
- Responsive design

### Dynamic Forms v1
- FormDefinition snippet for reusable forms
- 9 field types + 2 layout blocks
- DynamicFormBlock for page embedding
- Three presentation styles (inline, modal, sidebar)
- Email notifications and auto-replies
- Webhook integration
- Clone/duplicate forms
- Form usage tracking

### Integration
- Blog CTAs use DynamicFormBlock
- Deployed to Sage & Stone
- Lighthouse score ≥90
- ≥80% test coverage

## Metrics
- Blog posts: 5+ created
- Form definitions: 3+ created
- Lighthouse: 90+ across all metrics
- Test coverage: ≥80%
- Zero lost leads maintained"
```

**Document deployment:**
```bash
# Update deployment log
cat >> docs/ops-pack/deployment-log.md << EOF

## $(date +%Y-%m-%d) - Blog v1 + Dynamic Forms v1

**Deployed by:** [Your Name]
**Tag:** v1.0.0-blog-forms
**Environment:** Sage & Stone Production

### Deployed Features
- Blog v1 (BlogIndexPage, BlogPostPage, Category)
- Dynamic Forms v1 (FormDefinition, DynamicFormBlock, 11 field types)
- Email notifications and webhooks
- Performance optimizations

### Migration Summary
- Added FormDefinition model
- Added Category snippet
- Added BlogIndexPage and BlogPostPage models
- No data migrations required (backwards compatible)

### Validation Results
- Lighthouse (Blog Index): 95 Performance, 100 Accessibility, 100 Best Practices, 100 SEO
- Lighthouse (Blog Post): 93 Performance, 100 Accessibility, 100 Best Practices, 100 SEO
- All DoD criteria met
- Zero critical issues

### Rollback Plan
If issues arise, rollback to previous tag: v0.9.x
\`\`\`bash
git checkout [previous-tag]
# Redeploy
\`\`\`

EOF
```

## Notes for AI Agents

- **Final critical task** - validates entire implementation
- Follow deployment runbook exactly - don't skip steps
- Backup database before any deployment
- Test on staging first if available
- Create realistic sample content - demonstrates features
- Lighthouse audit must pass ≥90 on all metrics
- Document any deployment issues for future reference
- Verify email/webhook integration with real services
- Test with multiple browsers (Chrome, Firefox, Safari)
- Check mobile experience thoroughly
- Monitor logs for errors after deployment
- Have rollback plan ready if issues detected
- Celebrate successful deployment! 🎉
