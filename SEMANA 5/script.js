// Selección de elementos del DOM
const formProducto = document.getElementById('formProducto');
const nombreProducto = document.getElementById('nombreProducto');
const descProducto = document.getElementById('descProducto');
const catProducto = document.getElementById('catProducto');
const mensajeValidacion = document.getElementById('mensajeValidacion');
const listaProductos = document.getElementById('listaProductos');
const totalRegistros = document.getElementById('totalRegistros');

let contador = 0;

// Capturar el evento submit del formulario
formProducto.addEventListener('submit', function(event) {
    event.preventDefault(); // Evita que la página se recargue

    // Validación de campos vacíos
    if (nombreProducto.value.trim() === '' || descProducto.value.trim() === '' || catProducto.value === '') {
        mostrarMensaje('Por favor, complete todos los campos antes de registrar.', 'danger');
        return;
    }

    // Creación dinámica de elementos
    const colDiv = document.createElement('div');
    colDiv.className = 'col-md-4 mb-3'; 

    const cardDiv = document.createElement('div');
    cardDiv.className = 'card h-100 shadow-sm border-primary';

    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    const categoria = document.createElement('span');
    categoria.className = 'badge bg-secondary mb-2';
    categoria.textContent = catProducto.value;

    const titulo = document.createElement('h5');
    titulo.className = 'card-title text-primary';
    titulo.textContent = nombreProducto.value;

    const descripcion = document.createElement('p');
    descripcion.className = 'card-text';
    descripcion.textContent = descProducto.value;

    const btnEliminar = document.createElement('button');
    btnEliminar.className = 'btn btn-danger btn-sm w-100 mt-2';
    btnEliminar.textContent = 'Eliminar';
    
    // Evento click para eliminar
    btnEliminar.addEventListener('click', function() {
        listaProductos.removeChild(colDiv);
        contador--;
        actualizarContador();
        mostrarMensaje('Producto eliminado correctamente.', 'warning');
    });

    // Ensamblar estructura
    cardBody.appendChild(categoria);
    cardBody.appendChild(titulo);
    cardBody.appendChild(descripcion);
    cardBody.appendChild(btnEliminar);
    
    cardDiv.appendChild(cardBody);
    colDiv.appendChild(cardDiv);
    listaProductos.appendChild(colDiv);

    // Actualizar contador y limpiar formulario
    contador++;
    actualizarContador();
    formProducto.reset();
    
    mostrarMensaje('Producto registrado exitosamente.', 'success');
});

// Función para mostrar mensajes
function mostrarMensaje(texto, tipo) {
    mensajeValidacion.innerHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
            ${texto}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;
    
    setTimeout(() => {
        mensajeValidacion.innerHTML = '';
    }, 3000);
}

// Función para actualizar el contador
function actualizarContador() {
    totalRegistros.textContent = contador;
}