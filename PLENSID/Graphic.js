/* Copyright [2017] [Sid Mahapatra]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var vertex_src =
"      attribute vec3 aVertexPosition;" +
"      attribute vec2 tex_coord;" + 
"      varying highp vec2 vtex_coord;" + 
"      void main() {" +
"        vtex_coord = tex_coord;" +
"        gl_Position = vec4(aVertexPosition, 1.0);" +
"      }";

var gl = null;

var errors = [];

function checkgl() {
    var e = gl.getError(); // returns error information
    if(e) console.error("WebGL produced error " + errors[e] + " (" + e + ")");
}

function start() {
    // This is needed to work around the fact that Firefox doesn't
    // support range inputs.
    $('#pitch')[0].max = 0.3;

    $('#advanced_link').click(function(e) {
        $('#advanced_controls').toggle('fast');
    });

    var canvas = document.getElementById("glcanvas");

    gl = initWebGL(canvas); 
}

function initBuffers() {
    vertices = [
       -1.0, -1.0, 0.0,
        1.0, -1.0, 0.0,
        1.0,  1.0, 0.0,
       -1.0,  1.0, 0.0
    ];

    tcoords = [
        0, 0,
        1, 0,
        1, 1,
        0, 1
    ];

    //WebGLBuffer represents an opaque buffer object storing data such as vertices or colors
    vbuf = gl.createBuffer(); //creates and initializes a WebGLBuffer storing data such as vertices or colors.
    checkgl();
    //Buffer containing vertex attributes, such as vertex coordinates, texture coordinate data, or vertex color data
    gl.bindBuffer(gl.ARRAY_BUFFER, vbuf); // binds a given WebGLBuffer to a target
    checkgl();
    // Contents of the buffer are likely to be used often and not change often.
    //Contents are written to the buffer, but not read.
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices),
                  gl.STATIC_DRAW); //initializes and creates the buffer object's data store
    checkgl();
    tbuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, tbuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(tcoords),
                  gl.STATIC_DRAW);
    checkgl();
}

function setParam(name) {
    //WebGLUniformLocation represents the location of a uniform variable in a shader program
    var attrib = gl.getUniformLocation(prog, name); // returns a WebGLUniformLocation of a uniform variable in a given WebGLProgram
    var el = document.getElementById(name);
    var v = parseFloat(el.value); //parses a string and returns a floating point number
    //determines if the first character in the specified string is a number. If it is, it parses the string 
    //until it reaches the end of the number, and returns the number as a number, not as a string
    if($(el).hasClass("flipped")) 
        v = parseFloat(el.max) - v;
    gl.uniform1f(attrib, v); //specify values of uniform variables
    checkgl();
}

function draw() {
    // set the shader parameters
    $('input.param').each(function (i, p) {
        setParam(p.id);
    });

    // Actually draw
    gl.clearColor(0, 0, 0, 1.0); //specifies the color values used when clearing color buffers
    gl.clear(gl.COLOR_BUFFER_BIT); //clears buffers to preset values
    gl.activeTexture(gl.TEXTURE0); //specifies which texture unit to make active
    // The value is a gl.TEXTUREI where I is within the range from 0 to gl.MAX_COMBINED_TEXTURE_IMAGE_UNITS - 1

    // WebGLTexture represents an opaque texture object providing storage and state for texturing operations
    gl.bindTexture(gl.TEXTURE_2D, tx); //binds a given WebGLTexture to a target (binding point)
    tex_attr = gl.getUniformLocation(prog, "tex");
    gl.uniform1i(tex_attr, 0);
    
    checkgl();
    
    // DRAW!
    gl.bindBuffer(gl.ARRAY_BUFFER, vbuf);
    gl.vertexAttribPointer(vattr, 3, gl.FLOAT, false, 0, 0); //specifies the memory layout of the buffer holding the vertex attributes
    checkgl();
    gl.bindBuffer(gl.ARRAY_BUFFER, tbuf);
    gl.vertexAttribPointer(tattr, 2, gl.FLOAT, false, 0, 0); // uses 32-bit floating point number
    checkgl();
    //gl.disableVertexAttribArray(tattr);
    gl.drawArrays(gl.TRIANGLE_FAN, 0, 4); // renders primitives from array data
    // Triangle_Fan is a set of connected triangles that share one central vertex
    checkgl();
}

function loadTexture(url) {
    tx = gl.createTexture(); // creates and initializes a WebGLTexture object
    // HTMLImageElement interface provides special properties and methods  
    //for manipulating the layout and presentation of <img> elements
    img = new Image(); // creates a new HTMLImageElement instance
    img.onload = function () {
        gl.bindTexture(gl.TEXTURE_2D, tx); // A two-dimensional texture.
        checkgl();
        //Flips the source data along its vertical axis
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); // specifies the pixel storage modes. 
        //Red, green, blue and alpha components are read from the color buffer
        //  8 bits per channel for gl.RGBA
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE,
                      img); //specifies a two-dimensional texture image

        // Using Texture magnification filter
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);// set texture parameters
        //using Texture minification filter
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        // Wrapping function for texture coordinate s
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        // Wrapping function for texture coordinate t
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        checkgl();
        
        console.info("Texture loaded, about to draw...");

        draw();
    }
    img.src = url;
}

function readContents(iframe) {
    return iframe.document.getElementsByTagName("pre")[0].innerText;
}

function initWebGL(canvas) {
    try {
        // creates a WebGLRenderingContext object representing a three-dimensional rendering context
        //  provides the OpenGL ES 2.0 rendering context for the drawing surface of an HTML <canvas> element
        gl = canvas.getContext("experimental-webgl"); // returns a drawing context on the canvas
    }
    catch(e) {
        console.error("Error getting context.");
    }

    if(!gl) {
        console.error("Your browser doesn't appear to support WebGL.");
    }

    // initialize error strings
    for(x in gl) {
        errors[gl[x]] = x;
    }

    // initialize shaders
    vshade = makeShader(vertex_src, gl.VERTEX_SHADER);
    $.ajax({
        url: "Shader(s).txt",
        success: function(frag_src) {
            fshade = makeShader(frag_src, gl.FRAGMENT_SHADER);
            //WebGLProgram is a combination of two compiled WebGLShaders consisting of a vertex shader
            //and a fragment shader (both written in GLSL)
            prog = gl.createProgram(); //creates and initializes a WebGLProgram object
            
            gl.attachShader(prog, vshade); //attaches a fragment WebGLShader
            gl.attachShader(prog, fshade);
            gl.linkProgram(prog); //links a given WebGLProgram to the attached vertex and fragment shaders
             
            if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { // returns information about the given program
                // Returns a GLboolean indicating whether or not the last link operation was successful
                console.error("Unable to initialize the shader program.");
            }
            
            gl.useProgram(prog); //sets the specified WebGLProgram as part of the current rendering state
            
            // set up attributes
            // aVertexPosition is the name of the attribute variable whose location to get
            vattr = gl.getAttribLocation(prog, "aVertexPosition"); // returns the location of an attribute variable in a given WebGLProgram
            //vattr specifies the index of the vertex attribute to enable
            gl.enableVertexAttribArray(vattr); // turns the generic vertex attribute array on at a given index position
            checkgl();
            
            tattr = gl.getAttribLocation(prog, "tex_coord");
            gl.enableVertexAttribArray(tattr);
            checkgl();
            
            initBuffers();
            
            console.info("Loaded fragment shader and initialized buffers.");
            loadTexture("bird_decoded.jpg");
        }
    });

    return gl;
}

function makeShader(src, type) {
    //A Fragment Shader is the Shader stage that will process a Fragment generated by 
    //the Rasterization into a set of colors and a single depth value. 
    //The fragment shader is the OpenGL pipeline stage after a primitive is rasterized. 
    //For each sample of the pixels covered by a primitive, a "fragment" is generated.

    //The Vertex Shader is the programmable Shader stage in the rendering pipeline that 
    //handles the processing of individual vertices. Vertex shaders are fed Vertex Attribute data,
    //as specified from a vertex array object by a drawing command

    //Rasterisation (or rasterization) is the task of taking an image described in a vector
    //graphics format (shapes) and converting it into a raster image (pixels or dots) for output
    //on a video display or printer, or for storage in a bitmap file format.
    var shader = gl.createShader(type); // creates a WebGLShader
    checkgl();
    
    gl.shaderSource(shader, src); //sets the source code of a WebGLShader
    checkgl();
    
    gl.compileShader(shader); //compiles a GLSL shader into binary data
    checkgl();
    
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) { //returns information about the given shader
        console.error("An error occurred compiling the shaders: " //Returns a GLboolean indicating whether 
        //or not the last shader compilation was successful
                      + gl.getShaderInfoLog(shader)); //returns the information log for the specified WebGLShader object.
                       //It contains warnings, debugging and compile information.
        return null;
    }
    
    return shader;
}
