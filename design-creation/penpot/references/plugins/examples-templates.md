# Examples and templates

## 5.1. Examples

We've put together a handy list of some of the most common actions you can perform in penpot, and we've also included a helpful example for each one. We hope this makes it easier for you to create your plugins!

If you just want to get to the examples, you can go straight to the repository [here](https://github.com/penpot/penpot-plugins-samples/tree/main)

### Create a shape

One of the most basic things you can do in design is create a shape. It's really simple. In this example, we'll show you how to make a rectangle, but you can use the same principles to make other shapes. This makes it easy for you to add different shapes to your design, which is great for building more complex elements and layouts.

```js
// just replace
penpot.createRectangle();

// for one of these other options:
penpot.createEllipse();
penpot.createPath();
penpot.createBoard();
```

[Shape example](https://github.com/penpot/penpot-plugins-samples/tree/main/create-shape)

### Create a text

You'll learn how to insert text and explore a variety of styling options to customize it to your exact preferences. You'll discover how to adjust font, size, color, and more to create visually engaging text elements. You can also apply multiple styles within a single text string by styling different sections individually, giving you even greater control over your text design and allowing for creative, dynamic typographic effects.

[Text example](https://github.com/penpot/penpot-plugins-samples/tree/main/create-text)

### Group and ungroup shapes

It's really important to keep your layers organized if you want to keep your workflow clean and efficient. Grouping shapes together makes it much easier to manage and manipulate multiple elements as a single unit. This not only makes your design process much more streamlined, but it also helps you maintain a structured and organized layer hierarchy. When you need to make individual adjustments, you can easily ungroup these shapes, which gives you flexibility while keeping your workspace tidy and well-organized.

[Group and ungroup example](https://github.com/penpot/penpot-plugins-samples/tree/main/group-ungroup)

### Create flex layout

Flex Layout makes it simple to create designs that adapt and respond to different screens and devices. It automatically adjusts the positioning and sizing of content and containers, so you can resize, align, and distribute elements without any manual intervention.

[Flex layout example](https://github.com/penpot/penpot-plugins-samples/tree/main/create-flexlayout)

### Create grid layout

Grid Layout lets you create flexible designs that automatically adapt to different screen sizes and content changes. You can easily resize, fit, and fill content and containers with this feature, so you don't have to make manual adjustments and you get a seamless, responsive design experience.

[Grid layout example](https://github.com/penpot/penpot-plugins-samples/tree/main/create-gridlayout)

### Create a component

Using components is a great way to reuse objects or groups of objects, making sure everything looks the same and works well across your designs. This example shows you how to create a component, which lets you make your workflow easier by defining reusable design elements.

Just a friendly reminder that it's important to have the <b>library permissions</b> in the `manifest.json`.

[Components example](https://github.com/penpot/penpot-plugins-samples/tree/main/components-library)

### Create a colors library

Having quick access to your go-to colors and fonts can really help you work more efficiently, letting you build a solid set of assets with minimal effort. In this example, you'll see how to add a color to your library, so you'll have instant access whenever you need it. The same goes for typography assets—just replace createColor with createTypography. This flexibility means your most commonly used design elements are always at your fingertips, ready to enhance your creative workflow.

Just a friendly reminder that it's important to have the <b>library permissions</b> in the `manifest.json`.

```js
// just replace
penpot.library.local.createColor();

// for
penpot.library.local.createTypography();
```

[Colors library example](https://github.com/penpot/penpot-plugins-samples/tree/main/colors-library)

### Theme

Penpot has dark and light modes, and you can easily add this to your plugin so your interface adapts to both themes. When you add theme support, your plugin will automatically sync with Penpot's interface settings, so the user experience is consistent no matter which mode is selected. This makes your plugin look better and also ensures it stays in line with Penpot's overall design.

Just a heads-up: if you use the [plugin-styles library](https://styles-doc.plugins.penpot.app/), many elements will automatically adapt to dark or light mode without any extra effort from you. However, if you need to customize specific elements, be sure to use the selectors provided in the `styles.css` of the example.

[Theme example](https://github.com/penpot/penpot-plugins-samples/tree/main/theme)

### Use of third party API

Often, we want to make our plugins better by adding external libraries, new features, and functionalities. Here's an example of how to use the Picsum library. It shows how you can use third-party APIs to make your plugin development better. Use this as a reference to explore how you can add external resources to your projects.

[Third party API example](https://github.com/penpot/penpot-plugins-samples/tree/main/third-party-api)

### Interactive prototype

With the ability to create an interactive prototype, you can turn your design from a static layout into a dynamic, navigable experience. This lets users interact with the design in a more seamless way and gives them a better preview of the final product.

[Interactive prototype example](https://github.com/penpot/penpot-plugins-samples/tree/main/create-interactive-prototype)

### Add ruler guides

Ruler guides are great for aligning elements exactly where you want them. Check out how to add horizontal and vertical guides to your page or boards. This makes it easier to keep your design looking the same from one place to the next.

[Ruler guides example](https://github.com/penpot/penpot-plugins-samples/tree/main/create-ruler-guides)

### Create a comment

Comments are a great way for designers and team members to give each other feedback on a design right away. This example shows how to add comments to specific parts of a design, which makes it easier for everyone to work together and improve their workflow.

Just a friendly reminder that it's important to have the <b>comment permissions</b> in the `manifest.json`.

[Comments example](https://github.com/penpot/penpot-plugins-samples/tree/main/create-comments)

## 5.2. Templates

As we mentioned in the [Create a plugin](/plugins/create-a-plugin/) section, we've got two great options for you to get started with your plugin.
The first is a basic **Typescript** template with all the essential structure you'll need.
The second is the same, but uses one of the most popular frameworks like **Angular, Vue, or React**. We've included links to the repositories below:

- [Plugin Starter Template with plain Typescript](https://github.com/penpot/penpot-plugin-starter-template)

- [Plugin Starter Template using a framework](https://github.com/penpot/plugin-examples)
