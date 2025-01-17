# Contributing to cports

While Chimera is not made of only `cports`, most people will probably want
to contribute here.

## Getting started

First you will need to fork this repository on GitHub. This is not different
from any other project.

We suggest to avoid using GitHub's web editor for contributions, especially
for templates, since those need testing. Therefore, if you do not know at
least the basics of Git, use some of the public resources to get familiar.

Once you have that, clone your fork and prepare the changes.

## Preparing your changes

Whether you are creating a new template or modifying an existing one, you
should follow the manual (see `Manual.md`) which should be able to answer
all or at least most questions.

Always ensure to follow the expected style and other basics to make the
reviewer's job easier.

## Committing changes

Generally, you should have one commit per template. The commits should be
atomic, i.e. every commit should build on its own. When you have a batch
of templates and they depend on each other, order your commits properly.

Using a correct commit message is also important:

* New packages should use `category/pkgname: new package (<version>)`. For
  example, `main/bsdutils: new package (0.10.0)`.
* Updates should similarly use `category/pkgname: update to <version>`.
* Non-update changes to templates should use `category/pkgname: custom message`.
* Removals should use `category/pkgname: remove`.
* Changes to `cbuild` should use `cbuild: custom message`.

It is your responsibility to verify that submitted changes do build. If the
CI fails, fix any issues that you are capable of fixing yourself.

## Creating a pull request

Once you have committed your changes, create a GitHub pull request. The best
way to do that is to push your changes into a custom branch. When you `git push`
into that branch, the command line will offer you a link to create your PR.

## Getting review

If there are any issues with your PR, a reviewer will point them out and possibly
suggest changes. Follow any review instructions until the changes are approved.

There is no CLA in Chimera, likewise there is no copyright assignment or any
such thing.

## Getting your changes merged

Congratulations! At this point, your changes should have made them into the
repository. As always, do not hesitate to join us in one of our communication
channels if anything is unclear.
