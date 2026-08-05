# Design Tokens

Design tokens are the building blocks of all UI elements, the same tokens are used in designs, tools, and code. They include colors, typography, spacing, shadows, and any visual element that affects a layer: all these properties collectively make up a design system or a visual inheritance.

### Why Design Tokens?

Design tokens act as a single source of truth, a common language that can be translated and used in any other tool or framework capable of reading the token format. With Design Tokens, you can create, manage, and synchronize these visual elements within Penpot and across other design tools, keeping your designs consistent and making your workflows faster and easier to maintain.

You can also integrate Design Tokens with other core Penpot features, such as components and grid & flex layout, plus plugins will be able to access the tokens API (coming soon) making it even more powerful.

### W3C DTCG Format

Penpot Design Tokens adhere to the [Design Tokens Format Module](https://design-tokens.github.io/community-group/format/) and [its definitions](https://www.designtokens.org/glossary/), a draft by the [W3C DTCG](https://www.w3.org/community/design-tokens/). Penpot ensures compatibility across various disciplines, tools, and technologies by following the most standardized approach available for design tokens.

Tokens can be exported from Penpot or integrated into other tools directly, without conversion. Additionally, the knowledge gained from using Design Tokens in Penpot remains valuable, regardless of whether you continue using Penpot or a different tool or technology.

## Creating a token

You can create reusable and semantic tokens to be referenced in your designs at the **Tokens** panel. In this panel, you’ll find all the available types of tokens in Penpot arranged alphabetically, with existing tokens being shown at the top of the list.

To create a token, click on the + next to the type of token you want to create. You’ll then be prompted to define the token’s:

- **Name:** The name should be specific to that token, as it is not possible to create multiple tokens with the same name; for example, **dimension.small**.
- **Value:** The value you wish to attribute to the token; depending on the token type, values may be numerical or color spaces (Hex, RGB, RGBA, ARGB, HSL or HSLA).
- **Description:** You can also choose to add a description to your token.

Once you have named the token and assigned it a value, click **Save** to store the token and start referencing it.

Token value fields suggest existing tokens as you type. Pick a suggestion to insert a reference, or keep typing a custom value.

## Referencing tokens into values (aliases)

When assigning a value to a token, you can reference existing tokens - these are called aliases at the [DTCG Glossary](https://www.designtokens.org/glossary/).

For example, if you have created a **dimension.small** token, with a value of 64, you could create a **spacing.small** token with a value of `{dimension.small}`. The **spacing.small** token would thereby have a value of 64.

When referencing an existing token in the value of a new token, you must reference it within **{}**.

If the value of the referenced token changes, this will also change the value of the tokens where it is referenced.

References to existing tokens are case sensitive.

## Using math in token values

Token types with numerical values accept mathematical equations to calculate their values. This allows you to create dynamic relationships between tokens and build flexible design systems.

For example, if you create a **spacing.small** token with the value of **2**, and you want to create a **spacing.medium** token that is twice as large, you can write `{spacing.small} * 2` in its value. As a result, **spacing.medium** would have a value of **4**.

You can also reference other tokens in your equations. Say you have a **spacing.scale** token with a value of **2**. You could use this token in the equation to calculate the value of **spacing.medium** by writing `{spacing.small} * {spacing.scale}` in its value.

### Basic operators

Mathematical equations can be performed using these basic operators:

- `+` for addition
- `-` for subtraction
- `*` for multiplication
- `/` for division
- `%` for modulo (remainder)
- `^` for exponentiation

### Math functions

In addition to basic operators, you can use various math functions in your token values:

- `abs(x)` - absolute value
- `ceil(x)` - round up to nearest integer
- `floor(x)` - round down to nearest integer
- `round(x)` - round to nearest integer
- `max(x, y, ...)` - maximum value
- `min(x, y, ...)` - minimum value
- `sqrt(x)` - square root
- `pow(x, y)` - x raised to the power of y
- `log(x)` - natural logarithm
- `exp(x)` - e raised to the power of x
- `sin(x)` - sine
- `cos(x)` - cosine
- `tan(x)` - tangent
- `asin(x)` - arcsine
- `acos(x)` - arccosine
- `atan(x)` - arctangent
- `atan2(y, x)` - arctangent of y/x

### Syntax and best practices

When writing math equations in token values, keep these guidelines in mind:

- Simple equations can be written with or without brackets. For example, `8 * 8` and `(8 * 8)` both resolve to `64`.
- Complex formulas require spaces between operators to ensure tokens are transformed correctly. For example, use `8 * 8` instead of `8*8`.
- Reference tokens using curly braces: `{token.name}`.
- You can combine hard-coded values with token references: `{spacing.base} * 1.5`.

### Practical examples

Here are some common use cases for math in token values:

#### Round to the nearest whole number

When using multipliers that result in decimals, you can use the `round()` function to get whole numbers. For example, if **sizing.sm** has a value of **2**:

```
round({sizing.sm} * 1.33)
```

This calculates `2 * 1.33 = 2.66`, which rounds to **3**.

#### Create a percentage from a unitless number

You can convert unitless numbers to percentages. For example, a Number token called **lineHeights.heading.relaxed** with a value of **1.5** can be written in a Line Height token as:

```
{lineHeights.heading.relaxed} * 100%
```

This calculates a resolved value of **150%**.

#### Calculate maximum or minimum values

Use `max()` or `min()` to ensure values stay within bounds. For example:

```
max({spacing.base}, 8)
```

This ensures the spacing is at least 8, even if the base token is smaller.

## Editing a token

Tokens can be edited by right-clicking the token and selecting **Edit token**. This will allow you to change the tokens name, value and description. Value fields offer the same token suggestions as when creating a token. Once the changes are made, click **Save**.

When you rename a token that has references (like aliases, math operations, or applied tokens), Penpot will prompt you to remap those references to the new name. If you choose to remap, all references will be updated automatically, including token aliases, design tab inputs, tooltips, and any elements where the token is applied. If the file is a library, remapping will also update references in files that use that library. You can also choose not to remap if you prefer to keep the old references, though this will break the connections.

## Duplicating a token

Tokens can be duplicated by right-clicking the token you wish to duplicate and selecting **Duplicate token**. This will create a copy of the selected token within the same set, with `-copy` added to its name.

## Deleting a token

Tokens can be deleted by right-clicking the token you wish to delete and selecting **Delete token**.

## Available tokens

You can apply tokens to the properties of any [layer](/user-guide/designing/layers/). There are two ways to apply tokens to a selection:

- Right-click on tokens to specify a particular property that you want to apply.
- Left-click on tokens to apply the assumtion. Assumptions can vary across different token types. For example, for the **color** type the assumtion is that you want to apply the token as a **fill**.

Tokens can be applied to multiple selected elements, but not to groups.

### Applying tokens from the Design tab

Besides applying tokens from the Tokens panel, you can bind tokens from numeric and color fields in the Design sidebar.

Token selection is available for:

- **Size and position:** width, height, x, y
- **Rotation and border radius**
- **Layout spacing:** gaps, paddings, margins, min and max widths and heights
- **Typography:** letter spacing, line height, and composite typography tokens on text layers
- **Stroke width**
- **Shadows:** x, y, blur, spread
- **Blur** amount

Click the token control on a field to open a list of applicable tokens from your active sets and themes. Select a token to apply it; a token pill shows the bound token. Use the pill menu to detach the token when you need a custom value again.

On text layers, the Typography section shows a composite typography token row when one is applied. Open the token list from the section header to pick or switch tokens without going to the Tokens panel. Hover a token name to see its resolved values (font family, size, weight, and the rest).

When you multi-select text layers that share typography tokens, the Typography section shows the applied token. If the selection mixes different tokens, detach them from there or apply a new one to the whole selection.

Typography options in the dropdown list show resolved values on hover, so you can tell styles apart before applying them.

When a numeric field has a token applied, drag-to-change is disabled for that field. Edit the token or detach it first.

### Border radius

Border radius tokens allow you to define specific values for border-radius properties, offering flexibility in how you style the corners of elements.

#### Applying Border Radius Tokens

To apply the border radius token to an element, select the element and choose the token from the list:

- Clicking on a border radius token will apply it to all corners of the element simultaneously.
- Right-clicking on a border radius token, allows you to select which corners the token should be applied to.

### Color

Color tokens support color properties that can be applied to many different design elements, including boards, groups, shapes, and text.

You can define a color token’s value using:

1. **The color picker**, select the color switch to the left of the token **Value** input to open the color picker; here you’ll also be able to define the colors opacity.
2. **The color Spaces**, define your color token in the following color spaces:
   - Hex: #ff0000
   - RGB: rgb(255, 0, 0)
   - RGBA: rgba(255, 0, 0, 1)
   - ARGB: #80FFFF00 (also known as Hex8)
   - HSL: hsl(120, 50%, 50%)
   - HSLA: hsla(120, 50%, 50%, 1)

#### Applying Color Tokens

Color tokens can define a design element's **fill** or **stroke** color. To apply the color token to an element, select the element and choose the token from the list:

- Clicking on a color token will apply it to the element as a fill by default.
- Right-clicking on a color token, allows you to select whether it should be applied as a fill or stroke color.

### Dimension

Dimension tokens allow you to define an amount of distance that can be used to set the size, space, radius or position of specific elements within a design.

#### Applying Dimension Tokens

To apply a dimension token, select the element and choose the token from the list:

- Clicking on a dimension token will apply it to the element’s width and height by default.
- Right-clicking on a dimension token, allows you to select where you want the token to be used in the element. You can use it for:
  1. Sizing
  2. Spacing
  3. Border radius
  4. Stroke width
  5. X position
  6. Y position

#### Sizing (dimension)

The sizing property of the dimension token defines the height or width of design elements like boards, shapes, and groups.

When using dimension tokens for sizing, you can apply the token to an element's size by selecting:

- **All** to apply the same size value to both the width and height of an element;
- **Width** to apply the token value to the horizontal size of an element;
- **Height** to apply the token value to the vertical size of an element;

If you are working with flex-layout boards, you can also apply the token to an element’s size by selecting:

- **All** to apply the same size value to both the **Min width** and **Min height** of an element;
- **Min width** to define the smallest allowed horizontal size of an element but allow a larger size;
- **Min height** to define the smallest allowed vertical size of an element but allow a large size;
- **All** to apply the same size value to both the **Max width** and **Max height** of an element;
- **Max width** to define the largest allowed horizontal size of an element but allow a smaller size;
- **Max height** to define the largest allowed vertical size of an element but allow a smaller size.

If you apply the **min/max height/width properties** to a board before flex-layout is applied to it, you may have to remove and re-apply the token for it to take effect.

#### Spacing (dimension)

The spacing property of the dimension token defines the distance between elements and it must be applied to flex-layout boards.

If you apply the token to a board before flex-layout is applied to it, you may have to remove and re-apply the token for it to take effect.

When using dimension tokens for spacing, you can apply the token to an element's padding and gap. Specifically, you can select:

- **Gaps**
  - **All** to apply the gap to all sides of the element;
  - **Column Gap** to add a gap between child elements within a parent element;
  - **Row Gap** to add vertical space between rows on flex-layout board elements set to wrap.

- **Paddings & Margins:**
  - **Horizontal** applies to the left and right of the container;
  - **Vertical** and to the top and bottom sides of the container;
  - **Top, right, bottom or left** apply space to individual sides of the element.

#### Border radius (dimension)

The border radius property of the dimension token defines the roundness of the corner of elements like boards, shapes, and groups.

You can apply the border radius property by right-clicking on the dimension token and selecting:

- **All** to apply the radius to all sides of the selected element;
- **Top Left** to apply the radius to the top-left corner of the selected element;
- **Top Right** to apply the radius to the top-right corner of the selected element;
- **Bottom Right** to apply the radius to the bottom-right corner of the selected element;
- **Bottom Left** to apply the radius to the bottom-left corner of the selected element.

#### Stroke width (dimension)

The stroke width property specifies the thickness of a border for elements that already have a stroke property applied.

If you apply the border property to an element before it has a stroke applied to it, you may have to remove and re-apply the token for it to take effect.

#### X Position (dimension)

The X property specifies the position of the element on the X axis of the canvas.

#### Y Position (dimension)

The Y property specifies the position of the element on the Y axis of the canvas.

### Opacity

Opacity tokens allow you to define the opacity of a layer, ranging from fully opaque to fully transparent.

Opacity tokens can be applied to any design element that supports transparency. You can use any decimal value between 0 and 1 to set varying levels of opacity or you can use any value between 0 and 100 with **`%`** sign at the end of the value. For example, you can use **45%** which would resolve to **.45**.

#### Applying Opacity Tokens

To apply the opacity token to an element, select the element and click on the desired token.

### Rotation

Rotation tokens are used to define and standardize rotational values within a design system. These tokens represent rotation angles, typically measured in degrees, and can be applied to elements such as icons or images, to ensure consistent rotation throughout a design.

#### Applying Rotation Tokens

To apply a rotation token, select the element and choose the token from the list.

### Sizing

Sizing tokens can define various size-related design properties, namely the height and width of design elements.The sizing token supports numeric values, which include negative values.

#### Applying Sizing Tokens

To apply the sizing token to an element, select the element and choose the token from the list:

- Clicking on a sizing token will apply it to all sides of the element by default;
- Right-clicking on a sizing token, allows you to specify which side of the element the token should apply to:
  - **All** applies the same size value to both the width and height of an element;
  - **Width** applies the token to the horizontal size of an element;
  - **Height** applies the token to the vertical size of an element;

If you are working with flex-layout boards, you can also apply the token to an element’s size by selecting:

- **Min width** defines the smallest allowed horizontal size of an element, allowing larger sizes;
- **Min height** defines the smallest allowed vertical size of an element, allowing larger sizes;
- **Max width** defines the largest allowed horizontal size of an element, allowing smaller sizes;
- **Max height** defines the largest allowed vertical size of an element, allowing smaller sizes.

### Spacing

The spacing token defines the distance between design elements and supports numeric values, which include negative values. Spacing tokens must be applied to Flex Layout boards.

If you apply the token to a board before flex-layout is applied to it, you may have to remove and re-apply the token for it to take effect.

#### Applying Spacing Tokens

To apply the spacing token to an element, select the element and choose the token from the list:

- Clicking on a spacing token will apply it to all gaps (row and column).
- Right-clicking on a spacing token, allows you to specify which property of the element the token should apply to. In this menu, properties are divided by blocks. In each property you can choose to apply to ‘All’ sides in a specific property, or choose to apply them to individual sides:
- **Gaps:** Applies spaces between child elements within a parent container (both column and row gaps). This only works on flex and grid layouts.
- **Paddings & Margins:**
  - **Horizontal** applies to the left and right of the container;
  - **Vertical** and to the top and bottom sides of the container;
  - **Top, right, bottom or left** apply space to individual sides of the element.

### Stroke Width

The stroke width token, also known as the border width token, defines the thickness of a stroke around a design element. It can be applied to boards, groups, rectangles and text elements.

### Number token

Number tokens define the numeric value of properties that don’t require a unit of measurement.

The difference between a number token and a dimension token is that the first one has to be unitless.

The Number Token does not have a default property to apply to, so it can only be applied by right-clicking and selecting the specific property.

Number token is especially useful as a reference in other tokens, for math equations (**operands**), to create scales, for example font-size scales, or grid scales.

It can also be applied to Line Height –since this property works as a multiplier of the font size– or rotation property.

### Typography tokens

Typography tokens can only be applied to a text layer, but not to individual elements inside a text layer.
Applying a Typography Token will detach any Typography Style previously applied, and vice versa.

#### Font Family

As in other tokens, Font Family accepts references to other font family tokens.

Additionally, you can specify a prioritized list of Font Family names or generic names separated by commas (,), as in CSS. Penpot will use only the first font in the list, but this helps define your font fallbacks so developers can implement them accordingly.

```
  font-family: Lucida Console, Courier, monospace
```

When writing the string values of a **Font Family Token**, pay close attention to:

- Spelling
- Spacing
- Punctuation
- Use of capital letters

**Note:** You can quote font family names — especially those that contain spaces or special characters —
to follow **CSS best practices** or to align with the conventions used by your development team:

```
  font-family: "DM Sans", sans-serif;
```

If the Font Family does not exist in Penpot, when you apply the token you will see a “Missing font” message in the design panel input:

#### Font Size

Font size tokens define the vertical size of glyphs/characters as an individual property. In typography, the letter spacing and line height properties are related to the font size.

Font sizes are typically defined using a proportional scale. You can use math operations with references in order to create dynamic typography scales that follow a particular multiplier, like Golden Ratio.

**Tip:** Use [Number Tokens](#design-tokens-number) (unitless token) to create stunning typographic scales though design tokens:

Font size is a dimension-type token and should be defined in px (unitless values are computed as px) for now. To follow the DTGC format, in upcoming releases, units will be mandatory and rem units will be allowed.

You can use any dimension token as a reference in a font size token. Math operations are also allowed.

**Tip:** You can use a rounding function to round your resolved values and reduce decimals in math operations, since decimals are not ideal when using px:

`roundTo({values}, decimals)`

#### Font Weight

Font Weight defines the thickness of each character/glyph in the Font Family. Font Weight design decisions are typically used to communicate visual hierarchy or emphasize text elements.

Penpot combines Font Weight and Style as a single property written as a string value and it requires a match to the Font Family it is paired with, since not all font families have the same weight / styles.

The Token can be defined with a numeric value (100, 400, 900, etc) or a string name (Bold, Black, Thin, etc), and the font style (Italic), if needed.

**Note:** Font Family and Font Weight Tokens work as a pair in Penpot. This means you must consider the current Font Family in order to decide the Font Weight you want to use in your designs.

This token can be applied to text layers but the result depends on the Font Family in use.

##### Accepted values

Font Weight Token can be defined in numeric values or string values. Both values are accepted. When applied, a conversion will occur, transforming any string value to its corresponding numeric value:

| Numeric Value | String Value |
| --- | --- |
| 100 | Thin, Hairline |
| 200 | Extra Light, ExtraLight, extra-light, Ultra Light, UltraLight, ultra-light, extraleicht |
| 300 | Light, leicht |
| 400 | Regular, Normal, Book, buch |
| 500 | Medium, kraeftig, kräftig |
| 600 | Semibold, SemiBold, Semi Bold, semi-bold, DemiBold, Demi Bold, demi-bold, halbfett |
| 700 | Bold, dreiviertelfett |
| 800 | ExtraBold, Extra Bold, extra-bold, ultra-bold, UltraBold, Ultra Bold, fett |
| 900 | Black, Heavy, extrafett |
| 950 | Extra Black, extra-black, Ultra Black, ultra-black |

**Note:** values are case insensitive so for example `Regular` and `regular` will both work.

Any of these values can also include the Font Style *Italic*, if needed. Some examples of accepted values:

```
regular
Normal Italic
700
400 italic
Bold italic
ExtraBold Italic
```

#### Letter Spacing

Letter Spacing, also known as kerning, defines the horizontal distance between individual characters.

The default value is 0. In Penpot letter spacing is defined in px. In the token, you can use values in px or any reference to a Dimension / Spacing / Sizing / Letter Spacing Token.

This token can be applied directly to a text element or be used as a reference in a Typography Composite Token.

#### Text Case

Text Case defines that the system should transform the capitalization of letters in a text element regardless of how they are typed.

This property corresponds to `text-transform` in CSS.

Accepted values are `none`, `uppercase`, `lowercase` and `capitalize`. It also accepts references to another Text Case token.

This token can be applied directly to a text element or be used as a reference in a Typography Composite Token.

#### Text Decoration

Text Decoration defines an optional line as part of font styling properties, typically used to communicate the visual emphasis of a text.

Accepted values are `none`, `underline` and `strike-through`. It also accepts references to another Text Decoration token.

This token can be applied directly to a text element or be used as a reference in a Typography Composite Token.

### Typography composite token

**Typography tokens** are composite entities that group several text properties into a single token definition. They allow you to define and reuse complete text styles in a consistent way.

Each property within a typography token can either reference an existing [individual typography token](#design-tokens-typography) (for example, *font-size* or *font-family*) or use a hardcoded value. The behavior and syntax of individual typography tokens are described in the previous section of this guide.

#### Reference another Typography Composite Token

You can also reference another existing **Typography Composite Token** instead of defining each property manually. When doing so, Penpot resolves all individual properties from the referenced token.

#### Line height property

The **Typography Token** includes a *line-height* property, which is not available as an individual token. This is because line-height depends on the font size to be calculated properly. Make sure the *font-size* property is defined before setting *line-height*.

Accepted values for the line-height input:

- **Unitless number:** interpreted as a multiplier of the font size. This is Penpot’s default behavior.
- **Percentage (%):** converted internally to a multiplier.
- **Pixel (px) or rem value:** if using rem, Penpot calculates the proportion relative to the font size and converts it to a multiplier.
- **References:** you can also reference [number](#design-tokens-number) or [dimension](#design-tokens-dimensions) tokens.

#### Apply a Typography token

A **Typography composite token** can be applied to a full text layer to set all typography properties at once. This lets you manage complete text styles using a single token instead of combining multiple individual ones.

Apply it from the Tokens panel, or from the Typography section in the Design sidebar when a text layer is selected.

When applying a Typography composite token to a layer, any previously applied *Typography composite token* or *style* will be detached. The same happens in reverse. Only one of them can be active at a time.

### Shadow

Shadow tokens are composite entities that encapsulate the properties of one or more shadows into a single token definition. This token can contain a single shadow or an array of multiple shadows that can be reordered.

Shadow tokens support both **Drop Shadow** and **Inner Shadow** types. When creating or editing a shadow token, you can select the type of shadow you want to use. The default selection is Drop Shadow.

#### Shadow properties

Each shadow within a shadow token contains a set of properties that define how the shadow appears:

- **Color:** The color of the shadow. Accepts the same values as [color tokens](#design-tokens-color) (Hex, RGB, RGBA, ARGB, HSL, HSLA), and you can reference existing color tokens. The color picker is available when defining the value.
- **X offset:** The horizontal offset of the shadow. Can be unit or unitless, and accepts negative values. You can use a number or reference a [number](#design-tokens-number) or [dimension](#design-tokens-dimensions) token.
- **Y offset:** The vertical offset of the shadow. Can be unit or unitless, and accepts negative values. You can use a number or reference a [number](#design-tokens-number) or [dimension](#design-tokens-dimensions) token.
- **Blur:** The blur radius of the shadow. Can be unit or unitless. You can use a number or reference a [number](#design-tokens-number) or [dimension](#design-tokens-dimensions) token.
- **Spread:** The spread radius of the shadow. Can be unit or unitless. You can use a number or reference a [number](#design-tokens-number) or [dimension](#design-tokens-dimensions) token.
- **Type:** Whether the shadow is a drop shadow or an inner shadow. Selected via a dropdown menu, with Drop Shadow as the default.

Each property within a shadow token can reference existing tokens or be assigned hardcoded values. Shadows can also reference other shadow tokens (the type of shadow must match when using references).

Not all properties are mandatory to save a shadow token. Some can be empty (and will be computed as 0). Only the color property is mandatory. In an array of shadows, if any shadow does not have the color set, the form cannot be saved.

#### Creating shadow tokens

To create a shadow token, click on the **+** next to **Shadow** in the Tokens panel. Shadow tokens can be created in two ways:

- **Individual values:** You can create one shadow or multiple shadows with individual property values. Click the **+** button to add more shadows to the array. New shadows are added at the top of the list.
- **Single reference:** You can reference another existing shadow token. When using a single reference, you cannot add more than one shadow. The resolved value will display the shadow or list of shadows that the referenced token contains.

When creating a shadow with individual values, the color value starts empty, but the other inputs have default values (X: 4, Y: 4, Blur: 4, Spread: 0). You can reorder shadows by hovering over a shadow form and using the reorder button to drag it to a different position.

You can also reference another existing shadow token instead of defining each property manually. When doing so, Penpot resolves all shadow properties from the referenced token.

#### Applying shadow tokens

Shadow tokens can be applied to any layer type. Clicking on a shadow token will apply it to the selected layer. Right-clicking on a shadow token shows the context menu with the **Shadow** option to apply it.

Text elements in CSS do not support inner shadows, but Penpot does, since it uses the filter property internally instead of the box-shadow property.

When applying a shadow token, any existing shadow on the layer will be overridden (whether it's a raw shadow or an applied token shadow). If the token contains an array of shadows, each shadow will be added in the same order as in the creation form.

In Penpot, an element can have multiple shadows, but only one token of the same type can be applied. This means that applying a second shadow token would override the first one, regardless of how many shadows the shape currently has.

## Token Sets

Token Sets allow you to split your tokens up into multiple files in order to create organized groups or collections of tokens. It enables efficient management and customization within design files. For example you can group all your color sets, sizing sets or platform-specific sets. The purpose of tokens sets is to organize them in a way that matches your needs.

When you create your first token, a default set is created. You can rename, group or move it later. As you create new token sets, they’ll be added sequentially after existing ones. You can reorder token sets by dragging and dropping them.

The order of the token sets is essential! If you have tokens with the same name (and different values) across multiple sets, the tokens that are in the set that appears last in the list will override the previous ones - similar to how Cascading Style Sheets work.

When creating a token set, it’s recommended that you assign it a unique name to ensure clarity. Token set names are not included in individual token names by default so it is possible to have tokens with the same name belonging to different token sets.

Token sets can be enabled or disabled. If a set is disabled, its tokens will be excluded from the token resolution process.

### Creating Token Sets

There are two ways to create a token set at the **Tokens** tab:

1. Click on the **+** next to **Sets**;
2. Click on the **Create one** button.

You’ll then need to name your token set. Set names should be specific, as it is not possible to create multiple token sets with the same name.

When a token set is selected, the tokens within the selected set are displayed on the panel below.

### Editing Token Sets

Right-click a token set to perform these quick actions:

1. **Rename**: Give the set a new name and press Enter.
2. **Duplicate**: Make a copy of the set.
3. **Delete**: Remove the set permanently.

### 

Once you have created a token set, you can start creating tokens within that token set. To do so, simply select the token set and create a new token.

If a token with the same name already exists in another set, a new token can still be created in the current set.

### Creating Token Set Folders

To group token sets just use folder-style names. For example, naming your sets `Light/Global` and `Light/Colors` will create a folder called ***Light*** with two sets inside it: ***Global*** and ***Colors***.

## Token Themes

Themes are a way to configure your sets to be applied in a specific context, such as a brand, a mode or a touchpoint. Themes enable switching between different styles dynamically by applying different token values depending on the selected theme.

Themes are multidimensional, this means that you can have more than one theme active at the same time, combining the values of the active themes.

#### Theme groups

Using Theme Groups you can categorise your themes into groups. This will allow you to generate a number of combinations involving color themes, brands, platforms, density, and more. Using groups will reduce the need to create an excessive number of individual themes with every combination.

For example:

*Group - theme options*

- **Mode** - Light, Dark
- **Brand** - RedPlanet, YellowCab
- **Contrast** - High, Low, Dim
- **Platform** - Web, App

When you have various themes inside a group, only one of the themes in this group can be active.

Having your sets clubbed under groups makes it more accessible to switch from a matrix of themes.

### Creating Token Themes

To create a new theme, click the **Create one** button in the Themes section. You can create a group (this is optional) or add an existing one, and then you then need to assign a name to your theme and click on **Save Theme**.

Your new theme will now appear on the Theme lists. You’ll need to enable the tokens sets that you want to include in the theme, clicking on the button “no active sets”. Here you can also activate and deactivate it, as well as delete the theme.

### Editing Themes

In the **Themes** section, you can find a dropdown to activate and deactivate themes. If there are no active themes, the dropdown shows a message of: “no theme active”.

To edit existing themes, you can click on the **Edit** button next to the dropdown in the **Themes** section or open the dropdown and select **Edit themes**:

This action will open a modal window where you can activate or deactivate themes, as well as select which Token sets should be part of the theme.

1. You can enable and disable the themes.
2. Configure the token sets you want to be included in the theme.
3. Deletes the theme.
4. Creates a new theme.

### Grouping Themes

You can categorize your themes into groups. This allows you to generate a matrix of potential combinations involving color themes, brands, modes, and more.

1. Select a particular group.
2. Select the theme from the group.
3. You can define what token sets should be used as part of this theme option.
4. Click save theme to see the changes.
5. Cancel to clear the edits.
6. Delete.

## Importing and Exporting Tokens

You can export Tokens from Penpot and import them from your computer to a Penpot file. Tokens can be imported from the **Tools** option at the bottom of the **Tokens** tab.

You can also [import tokens from a connected shared library](/user-guide/design-systems/libraries/#import-tokens-from-library) using the Libraries modal. That import uses the library's full token definition (sets and themes included) and replaces the tokens already in your file.

The **Import** functionality allows you to upload and replace the global token set using a single file or a folder with multiple files in it.

These features support JSON files formatted according to specific guidelines and preserve the ability to undo changes if needed.

1. **Import:** Click **Tools**, then select **Import** to view import options.
2. **Export:** Click **Tools**, then select **Export** to view export options.

### Import Options

#### ZIP file

You can import tokens from a **.zip** file. This file can either contain a single JSON file or a folder structure with multiple files. The ZIP import option provides flexibility for organizing your tokens before importing them into Penpot.

- If the ZIP contains a single JSON file, it will be imported as a single set of tokens.
- If the ZIP contains a folder structure, each file and folder will be interpreted as separate token sets, following the same rules as the multifile import.

#### Single JSON file

You can import a JSON file comprising all tokens, token sets and token themes.

When importing a single file, the first-level keys of the json file will be interpreted as the set name.

```
  {
    "Global": {
      // first-level key will be interpreted as set name
      "color": {
        "300": {
          "$value": "red",
          "$type": "color",
          "$description": "my token description"
        }
      }
    },
    "Brands/A": {
      // first-level key will be interpreted as set name
      "color": {
        "accent": {
          "$value": "{red}",
          "$type": "color",
          "$description": "my token description"
        }
      }
    },
    "Brands/B": {
      // first-level key will be interpreted as set name
      "color": {
        "accent": {
          "$value": "#fabada",
          "$type": "color",
          "$description": "my token description"
        }
      }
    }
  }
```

#### Multifile

Imports a folder containing multiple JSON files (one per Token Set) and additional files like `$themes.json` or `$metadata.json` configurations. When importing multiple files, the name and path of the individual json files inside the folder will be interpreted as set names. These files should only contain tokens.

Multifile folder structure example:

```` ```
    folder/
    ├── global/
    │   ├── colors.json		  // can only contain tokens
    │   └── dimension.json	// can only contain tokens
    ├── mode/
    │   ├── dark.json       // can only contain tokens
    │   └── light.json      // can only contain tokens
    ├── $themes.json        // themes config
    └── $metadata.json      // other metadata config
``` ````

The main folder name won’t be used to build token set names, so in this example, **folder** will be ignored in the set names.

### Export Options

Just like with importing, you can export tokens, themes and sets either in a single JSON file or in multiple files. There is no difference in the content being exported; the choice depends on your team's preferences for file organization: a single file with all the tokens, sets and themes, or a folder structure with separated JSON files organized by sets.

In both cases you can preview the result of the export options:

## Token groups

Token names are rarely short and simple. They often contain multiple sections that represent token type, state, property, variant, and more. To help manage this complexity, Penpot automatically organizes tokens into groups based on the structure of their names.

### How token groups work

When Penpot encounters a dot (`.`) in a token name, it breaks down the name and structures it as nested groups. For example, a token named `button.primary.default.background-color` is organized into groups like this:

- **button** (group)
- → **primary** (group)
- → → **default** (group)
- → → → **background-color** (token)

If you have another token like `button.primary.hover.background-color`, it shares the same group structure (`button.primary`) and appears nested within those groups.

This structure matches how tokens are organized in JSON format. When you export tokens, a token like `button.primary.default.background-color` is structured like this:

```
{
  "button": {
    "primary": {
      "default": {
        "background-color": {
          "$value": "#f00",
          "$type": "color"
        }
      }
    }
  }
}
```

### Visual appearance

In the Tokens panel, token groups appear as nested, collapsible folders. Only the last segment of the token name (the actual token) appears as a pill. The segments before it appear as group folders that you can expand or collapse.

When you create a new token, Penpot automatically unfolds the required path so you can see your newly created token. If you manually unfold a group path, it stays open even when you navigate to other areas of the app (this state resets if you reload the page).

### Working with token groups

Token pills keep the same actions as before: you can delete, edit, and duplicate tokens from the context menu. When editing a token name, you'll see the full token path including all group segments.

#### Moving tokens between groups

When you edit a token name and change the group segments, the token moves to its new group automatically. If the new group doesn't exist, Penpot creates it. If the group already exists, the token is moved there.

For example, if you rename `color.background.secondary` to `c.bg.sec`, the token moves from the `color.background` group to a new `c.bg` group.

#### Deleting token groups

When you delete a token, if it's the last token in its group, the empty group is automatically removed as well. You can also delete entire token groups directly, which removes all tokens within that group.

Deleting a token group removes all tokens it contains. Make sure you want to delete all tokens in a group before removing it.
