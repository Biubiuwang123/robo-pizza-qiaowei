# Robo Orders Pizza

**Live: https://robo.qiaowei.wang**

**A plain-language, hands-on tour of how identity, certificates, and secrets fit together on AWS — told through a robot ordering pizza.**

> I work at Amazon. This is a personal learning project built only from public AWS
> documentation and pricing. Views are my own and do not represent Amazon or AWS.
> Not affiliated with or endorsed by AWS.

## The story

Maple Hill Elementary is throwing a class party, and the teacher sends **Robo**, the
school's helper robot, to order pizza. Getting it done safely takes four things that are
usually invisible: a sign-in, a badge, a locked box, and a staff roster. Each one gets a
short interactive scene you can play, break, and fix.

| # | Scene | What you do | On AWS |
|---|---|---|---|
| 1 | Who's at the door? | Sign the teacher up and in; watch her wristband expire | Amazon Cognito |
| 2 | Is that badge real? | Inspect a website's badge, catch impostors, earn a badge, fast-forward time | AWS Certificate Manager, AWS Private CA |
| 3 | The locked box | Hide a password, let only Robo open it, change it without breaking anything | AWS Secrets Manager |
| 4 | The staff roster | Add or remove a teacher once and watch every system follow | AWS Directory Service |

Each scene starts from the problem, not the product: what is the smallest thing that
would solve it? The AWS name comes at the end.

## Status

Early build. Chapters arrive one at a time.

- [x] Landing page — live at https://robo.qiaowei.wang
- [ ] Scene 1 — Who's at the door?
- [x] Scene 2 — Is that badge real? (in review)
- [ ] Scene 3 — The locked box
- [ ] Scene 4 — The staff roster
