// Selección de elementos del DOM
const formProducto = document.getElementById('formProducto');
const nombreProducto = document.getElementById('nombreProducto');
const descProducto = document.getElementById('descProducto');
const catProducto = document.getElementById('catProducto');
const mensajeValidacion = document.getElementById('mensajeValidacion');
const listaProductos = document.getElementById('listaProductos');
const totalRegistros = document.getElementById('totalRegistros');
const estadoInventario = document.getElementById('estadoInventario');

// ============================================
// "BASE DE DATOS" SIMULADA
// En una futura migración a Flask, este arreglo
// vendría de una base de datos real (SQLite, etc.)
// y se pasaría a la plantilla con render_template()
// ============================================
let productos = [
    { id: 1, nombre: 'Laptop HP', descripcion: 'Laptop para oficina con 8GB RAM', categoria: 'Electrónica' },
    { id: 2, nombre: 'Silla ergonómica', descripcion: 'Silla para oficina con soporte lumbar', categoria: 'Oficina' },
    { id: 3, nombre: 'Lámpara LED', descripcion: 'Lámpara de escritorio ajustable', categoria: 'Hogar' }
];

// ============================================
// VALIDACIONES DINÁMICAS EN TIEMPO REAL
// ============================================

// Función para mostrar mensaje de error debajo de un campo específico
function mostrarMensajeCampo(campo, mensaje) {
    // Eliminar mensaje anterior si existe
    const mensajeAnterior = campo.parentElement.querySelector('.invalid-feedback');
    if (mensajeAnterior) {
        mensajeAnterior.textContent = mensaje;
    } else {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = mensaje;
        campo.parentElement.appendChild(feedback);
    }
}

// Función para limpiar validación de un campo
function limpiarValidacion(campo) {
    campo.classList.remove('is-invalid', 'is-valid');
    const feedback = campo.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.textContent = '';
    }
}

// Validación mientras escribe - Evento input
nombreProducto.addEventListener('input', function() {
    if (this.value.trim().length >= 3) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
        const feedback = this.parentElement.querySelector('.invalid-feedback');
        if (feedback) feedback.textContent = '';
    } else if (this.value.trim().length > 0) {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'El nombre debe tener al menos 3 caracteres.');
    } else {
        limpiarValidacion(this);
    }
});

descProducto.addEventListener('input', function() {
    if (this.value.trim().length >= 10) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
        const feedback = this.parentElement.querySelector('.invalid-feedback');
        if (feedback) feedback.textContent = '';
    } else if (this.value.trim().length > 0) {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'La descripción debe tener al menos 10 caracteres.');
    } else {
        limpiarValidacion(this);
    }
});

catProducto.addEventListener('change', function() {
    if (this.value !== '') {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
        const feedback = this.parentElement.querySelector('.invalid-feedback');
        if (feedback) feedback.textContent = '';
    } else {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'Debe seleccionar una categoría.');
    }
});

// Validación al perder el foco - Evento blur
nombreProducto.addEventListener('blur', function() {
    if (this.value.trim() === '') {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'Este campo es obligatorio.');
    } else if (this.value.trim().length < 3) {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'El nombre debe tener al menos 3 caracteres.');
    }
});

descProducto.addEventListener('blur', function() {
    if (this.value.trim() === '') {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'Este campo es obligatorio.');
    } else if (this.value.trim().length < 10) {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'La descripción debe tener al menos 10 caracteres.');
    }
});

catProducto.addEventListener('blur', function() {
    if (this.value === '') {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
        mostrarMensajeCampo(this, 'Debe seleccionar una categoría.');
    }
});

// ============================================
// RENDERIZADO DINÁMICO DE PRODUCTOS
// Recorre el arreglo "productos" con forEach
// (estructura repetitiva) y genera las tarjetas.
// En Flask/Jinja2 esto sería:
// {% for producto in productos %} ... {% endfor %}
// ============================================
function renderizarProductos() {
    listaProductos.innerHTML = '';

    productos.forEach(function(producto) {
        const colDiv = document.createElement('div');
        colDiv.className = 'col-md-4 mb-3';

        const cardDiv = document.createElement('div');
        cardDiv.className = 'card h-100 shadow-sm border-primary';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const categoria = document.createElement('span');
        categoria.className = 'badge bg-secondary mb-2';
        categoria.textContent = producto.categoria;

        const titulo = document.createElement('h5');
        titulo.className = 'card-title text-primary';
        titulo.textContent = producto.nombre;

        const descripcion = document.createElement('p');
        descripcion.className = 'card-text';
        descripcion.textContent = producto.descripcion;

        const btnEliminar = document.createElement('button');
        btnEliminar.className = 'btn btn-danger btn-sm w-100 mt-2';
        btnEliminar.textContent = 'Eliminar';

        // Evento click para eliminar (filtra el arreglo por id)
        btnEliminar.addEventListener('click', function() {
            productos = productos.filter(function(p) {
                return p.id !== producto.id;
            });
            renderizarProductos();
            mostrarMensaje('Producto eliminado correctamente.', 'warning');
        });

        cardBody.appendChild(categoria);
        cardBody.appendChild(titulo);
        cardBody.appendChild(descripcion);
        cardBody.appendChild(btnEliminar);
        cardDiv.appendChild(cardBody);
        colDiv.appendChild(cardDiv);
        listaProductos.appendChild(colDiv);
    });

    actualizarContador();
    actualizarEstadoInventario();
}

// ============================================
// ESTRUCTURA CONDICIONAL SEGÚN EL ESTADO DE LOS DATOS
// (independiente del mensaje de éxito/error del
// formulario, para que no se sobrescriban entre sí)
// ============================================
function actualizarEstadoInventario() {
    if (productos.length === 0) {
        estadoInventario.innerHTML = `
            <div class="alert alert-info" role="alert">
                No hay productos registrados todavía.
            </div>
        `;
    } else if (productos.length < 3) {
        estadoInventario.innerHTML = `
            <div class="alert alert-warning" role="alert">
                Inventario bajo. Se recomienda registrar más productos.
            </div>
        `;
    } else {
        estadoInventario.innerHTML = '';
    }
}

// ============================================
// CAPTURAR EVENTO SUBMIT DEL FORMULARIO
// ============================================
formProducto.addEventListener('submit', function(event) {
    event.preventDefault(); // Evita que la página se recargue
    
    // Bandera para validar todo
    let formularioValido = true;
    
    // Validación de campos vacíos
    if (nombreProducto.value.trim() === '') {
        nombreProducto.classList.remove('is-valid');
        nombreProducto.classList.add('is-invalid');
        mostrarMensajeCampo(nombreProducto, 'Este campo es obligatorio.');
        formularioValido = false;
    } else if (nombreProducto.value.trim().length < 3) {
        nombreProducto.classList.remove('is-valid');
        nombreProducto.classList.add('is-invalid');
        mostrarMensajeCampo(nombreProducto, 'El nombre debe tener al menos 3 caracteres.');
        formularioValido = false;
    } else {
        nombreProducto.classList.remove('is-invalid');
        nombreProducto.classList.add('is-valid');
    }
    
    // Validación de descripción
    if (descProducto.value.trim() === '') {
        descProducto.classList.remove('is-valid');
        descProducto.classList.add('is-invalid');
        mostrarMensajeCampo(descProducto, 'Este campo es obligatorio.');
        formularioValido = false;
    } else if (descProducto.value.trim().length < 10) {
        descProducto.classList.remove('is-valid');
        descProducto.classList.add('is-invalid');
        mostrarMensajeCampo(descProducto, 'La descripción debe tener al menos 10 caracteres.');
        formularioValido = false;
    } else {
        descProducto.classList.remove('is-invalid');
        descProducto.classList.add('is-valid');
    }
    
    // Validación de categoría
    if (catProducto.value === '') {
        catProducto.classList.remove('is-valid');
        catProducto.classList.add('is-invalid');
        mostrarMensajeCampo(catProducto, 'Debe seleccionar una categoría.');
        formularioValido = false;
    } else {
        catProducto.classList.remove('is-invalid');
        catProducto.classList.add('is-valid');
    }
    
    // Si hay errores, mostrar mensaje general y detener
    if (!formularioValido) {
        mostrarMensaje('Por favor, corrija los errores antes de registrar.', 'danger');
        return;
    }
    
    // ============================================
    // REGISTRO DINÁMICO: se agrega al arreglo
    // "productos" y se vuelve a renderizar todo
    // con renderizarProductos()
    // ============================================
    const nuevoProducto = {
        id: Date.now(),
        nombre: nombreProducto.value.trim(),
        descripcion: descProducto.value.trim(),
        categoria: catProducto.value
    };

    productos.push(nuevoProducto);
    renderizarProductos();

    formProducto.reset();
    
    // Limpiar clases de validación
    nombreProducto.classList.remove('is-valid', 'is-invalid');
    descProducto.classList.remove('is-valid', 'is-invalid');
    catProducto.classList.remove('is-valid', 'is-invalid');
    
    // Limpiar mensajes de error
    const mensajesError = document.querySelectorAll('.invalid-feedback');
    mensajesError.forEach(msg => msg.textContent = '');
    
    mostrarMensaje('Producto registrado exitosamente.', 'success');
});

// ============================================
// FUNCIÓN PARA MOSTRAR MENSAJES
// ============================================
function mostrarMensaje(texto, tipo) {
    mensajeValidacion.innerHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
            ${texto}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    setTimeout(() => {
        mensajeValidacion.innerHTML = '';
    }, 3000);
}

// ============================================
// FUNCIÓN PARA ACTUALIZAR EL CONTADOR
// ============================================
function actualizarContador() {
    totalRegistros.textContent = productos.length;
}

// ============================================
// RENDERIZADO INICIAL AL CARGAR LA PÁGINA
// ============================================
renderizarProductos();
