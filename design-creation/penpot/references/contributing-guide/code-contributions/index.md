# Core code contributions

Details to know how to improve Penpot's core code

Thinking of contributing to Penpot core but not sure where to start? We’ve made a curated selection of enhancements to help you with that. We believe that these tasks should be a great way to get started with Penpot development and quickly become an active contributor.
  
  
[Here’s the list of enhancements labeled as "good first issue"](https://github.com/penpot/penpot/contribute)

### Technical guide

Go to the [Technical guide](/technical-guide) to get detailed explanations about how to get Penpot application and run it locally, to test it or make changes to it.

### Pull requests

If you want propose a change or bug fix with the Pull-Request system firstly you should carefully read the [DCO section](#code-contributions-dco) and format your commits accordingly.

If you intend to fix a bug it's fine to submit a pull request right away but we still recommend to file an issue detailing what you're fixing. This is helpful in case we don't accept that specific fix but want to keep track of the issue.

If you want to implement or start working in a new feature, please open a **question** / **discussion** issue for it. No pull-request will be accepted without previous chat about the changes, independently if it is a new feature, already planned feature or small quick win.

If is going to be your first pull request, You can learn how from [this free video series](https://app.egghead.io/playlists/how-to-contribute-to-an-open-source-project-on-github).

We will use the `easy fix` mark for tag for indicate issues that are easy for beginners.

### Commit message guidelines

We have very precise rules over how our git commit messages can be formatted.

The commit message format is:

```
<type>  <subject>

[body]

[footer]
```

Where type is:

- `:bug:` a commit that fixes a bug
- `:sparkles:` a commit that adds an improvement
- `:tada:` a commit with new feature
- `:recycle:` a commit that introduces a refactor
- `:lipstick:` a commit with cosmetic changes
- `:ambulance:` a commit that fixes critical bug
- `:books:` a commit that improves or adds documentation
- `:construction:` a wip commit
- `:construction_worker:` a commit with CI related stuff
- `:boom:` a commit with breaking changes
- `:wrench:` a commit for config updates
- `:zap:` a commit with performance improvements
- `:whale:` a commit for docker related stuff
- `:rewind:` a commit that reverts changes
- `:paperclip:` a commit with other not relevant changes
- `:arrow_up:` a commit with dependencies updates

More info:

- <https://gist.github.com/parmentf/035de27d6ed1dce0b36a>
- <https://gist.github.com/rxaviers/7360908>

The subject should be:

- Use the imperative mood.
- Capitalize the first letter.
- Don't put a period at the end of the subject line.
- Put a blank line between the subject line and the body.

### Developer's Certificate of Origin (DCO)

By submitting code you are agree and can certify the below:

```
Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

Then, all your code patches (**documentation are excluded**) should contain a sign-off at the end of the patch/commit description body. It can be automatically added on adding `-s` parameter to `git commit`.

This is an example of the aspect of the line:

```
Signed-off-by: Andrey Antukh
```

Please, use your real name (sorry, no pseudonyms or anonymous contributions are allowed).
