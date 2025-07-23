import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer';
import getLayoutedElements from '../utils/layout';

interface GraphCanvas3DProps {
    nodes: any[];
    edges: any[];
    onNodeClick: (node: any) => void; // Added onNodeClick prop
}

const GraphCanvas3D: React.FC<GraphCanvas3DProps> = ({ nodes, edges, onNodeClick }) => {
    const mountRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!mountRef.current) return;

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f0f0); // Light grey background

        const camera = new THREE.PerspectiveCamera(75, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000);
        camera.position.z = 300; // Adjusted camera position

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
        mountRef.current.appendChild(renderer.domElement);

        // CSS2DRenderer for labels
        const labelRenderer = new CSS2DRenderer();
        labelRenderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
        labelRenderer.domElement.style.position = 'absolute';
        labelRenderer.domElement.style.top = '0px';
        labelRenderer.domElement.style.pointerEvents = 'none'; // Allow interaction with WebGL below
        mountRef.current.appendChild(labelRenderer.domElement);

        // Camera controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true; // Smooth damping
        controls.dampingFactor = 0.05;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.8); // Brighter ambient light
        scene.add(ambientLight);
        const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.6);
        directionalLight1.position.set(1, 1, 1).normalize();
        scene.add(directionalLight1);
        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight2.position.set(-1, -1, -1).normalize();
        scene.add(directionalLight2);

        // Apply 2D layout to get initial positions
        const { nodes: layoutedNodes } = getLayoutedElements(nodes, edges, 'LR'); // Use LR for a horizontal layout

        // Store node meshes and their original data for raycasting
        const nodeMeshes: THREE.Mesh[] = [];
        const nodeDataMap = new Map<string, any>(); // Map mesh.uuid to original node data

        // Create nodes
        const nodeGeometry = new THREE.SphereGeometry(10, 32, 32); // Slightly larger nodes
        const nodeMaterial = new THREE.MeshPhongMaterial({ color: 0x4a90e2 }); // Primary color

        const nodeGroup = new THREE.Group(); // Group to hold all nodes for easier bounding box calculation
        layoutedNodes.forEach(node => {
            const nodeMesh = new THREE.Mesh(nodeGeometry, nodeMaterial);
            // Scale down layouted positions to fit 3D view better
            nodeMesh.position.set(node.position.x * 0.8, node.position.y * 0.8, 0); // Set Z to 0 for a flatter initial view
            nodeMesh.userData.nodeId = node.id; // Store original node ID in userData
            nodeGroup.add(nodeMesh); // Add to group instead of scene directly
            nodeMeshes.push(nodeMesh);
            nodeDataMap.set(node.id, node); // Store original node data by its ID

            // Create CSS2D label
            const nodeDiv = document.createElement('div');
            nodeDiv.className = 'node-label';
            nodeDiv.textContent = node.data.label;
            const nodeLabel = new CSS2DObject(nodeDiv);
            nodeLabel.position.set(nodeMesh.position.x, nodeMesh.position.y + 20, nodeMesh.position.z); // Position label above node
            nodeGroup.add(nodeLabel); // Add to group
        });
        scene.add(nodeGroup); // Add the group to the scene

        // Calculate bounding box and fit camera
        if (layoutedNodes.length > 0) {
            const boundingBox = new THREE.Box3().setFromObject(nodeGroup);
            const center = new THREE.Vector3();
            boundingBox.getCenter(center);
            const size = new THREE.Vector3();
            boundingBox.getSize(size);

            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraZ *= 1.2; // Add some padding

            camera.position.set(center.x, center.y, center.z + cameraZ);
            camera.lookAt(center);
            controls.target.copy(center);
            controls.update();
        }

        // Create edges
        const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x888888, linewidth: 2 }); // Thicker lines
        edges.forEach(edge => {
            const sourceNodeMesh = nodeMeshes.find(mesh => mesh.userData.nodeId === edge.source);
            const targetNodeMesh = nodeMeshes.find(mesh => mesh.userData.nodeId === edge.target);
            if (sourceNodeMesh && targetNodeMesh) {
                const points = [sourceNodeMesh.position, targetNodeMesh.position];
                const edgeGeometry = new THREE.BufferGeometry().setFromPoints(points);
                const line = new THREE.Line(edgeGeometry, edgeMaterial);
                scene.add(line);
            }
        });

        // Raycasting for node clicks
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        const onCanvasClick = (event: MouseEvent) => {
            // Calculate mouse position in normalized device coordinates (-1 to +1)
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);

            const intersects = raycaster.intersectObjects(nodeMeshes);

            if (intersects.length > 0) {
                const clickedMesh = intersects[0].object as THREE.Mesh;
                const nodeId = clickedMesh.userData.nodeId;
                const nodeData = nodeDataMap.get(nodeId);
                if (nodeData) {
                    onNodeClick(nodeData);
                }
            }
        };

        renderer.domElement.addEventListener('click', onCanvasClick);

        // Animation loop
        const animate = () => {
            requestAnimationFrame(animate);
            controls.update(); // Only required if controls.enableDamping or controls.autoRotate are set to true
            renderer.render(scene, camera);
            labelRenderer.render(scene, camera);
        };
        animate();

        // Handle resize
        const handleResize = () => {
            if (mountRef.current) {
                camera.aspect = mountRef.current.clientWidth / mountRef.current.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
                labelRenderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
            }
        };
        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);
            renderer.domElement.removeEventListener('click', onCanvasClick); // Remove event listener
            if (mountRef.current) {
                mountRef.current.removeChild(renderer.domElement);
                mountRef.current.removeChild(labelRenderer.domElement);
            }
            // Dispose of Three.js objects to prevent memory leaks
            scene.traverse((object) => {
                if (object instanceof THREE.Mesh) {
                    object.geometry.dispose();
                    if (Array.isArray(object.material)) {
                        object.material.forEach(material => material.dispose());
                    } else if (object.material) {
                        object.material.dispose();
                    }
                }
            });
            renderer.dispose();
            controls.dispose();
        };
    }, [nodes, edges, onNodeClick]); // Added onNodeClick to dependencies

    return <div ref={mountRef} style={{ width: '100%', height: '100%', position: 'relative' }} />;
};

export default GraphCanvas3D;
