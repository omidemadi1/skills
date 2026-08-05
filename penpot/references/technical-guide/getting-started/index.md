# Self-hosting Guide

This guide explains how to get your own Penpot instance, running on a machine you control,
to test it, use it by you or your team, or even customize and extend it any way you like.

For additional context, see the post [How to self-host Penpot: A technical implementation guide](https://penpot.app/blog/how-to-self-host-penpot/) on the Penpot blog.

<strong>The experience stays the same, whether you use
Penpot [in the cloud](https://design.penpot.app)
or self-hosted.</strong>

Docker images are published shortly after the SaaS update:
[Why do self hosted versions lag behind new releases?](https://community.penpot.app/t/why-do-self-hosted-versions-lag-behind-new-releases/9897)

These are the main options to configure your Penpot instance:

1. Deploy with [docker compose][2]
2. Use Kubernetes in its different flavors:
    - Deploy the [official Helm Chart][3]
    - Deploy in [Openshift][4]
    - Deploy in [Rancher][5]
3. Other official options:
    - [Elestio][6]
    - [Truenas][7]

Or you can try [other options][1], offered by Penpot community.

[1]: /technical-guide/getting-started/unofficial-options/
[2]: /technical-guide/getting-started/docker/
[3]: /technical-guide/getting-started/kubernetes/
[4]: /technical-guide/getting-started/kubernetes/#using-openshift%3F
[5]: /technical-guide/getting-started/kubernetes/#using-rancher%3F
[6]: /technical-guide/getting-started/elestio/
[7]: https://apps.truenas.com/catalog/penpot/
