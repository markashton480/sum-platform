/**
 * Name: Navigation JS
 * Path: core/sum_core/static/sum_core/js/navigation.js
 * Purpose: Minimal JavaScript for mobile menu toggle and dropdown behaviour.
 * Family: SUM Platform – Navigation System
 * Dependencies: None (vanilla JS)
 */

(function() {
    'use strict';

    // =============================================================================
    // Selectors
    // =============================================================================
    const SELECTORS = {
        menuBtn: '#menuBtn, .menu-btn',
        navLinks: '#navLinks, .nav-links',
        dropdownToggle: '.nav-dropdown__toggle',
        dropdownMenu: '.nav-dropdown__menu',
        dropdown: '.nav-dropdown',
        header: '.header'
    };

    // =============================================================================
    // State
    // =============================================================================
    let mobileMenuOpen = false;

    // =============================================================================
    // Helper Functions
    // =============================================================================

    /**
     * Close all dropdown menus
     */
    function closeAllDropdowns() {
        document.querySelectorAll(SELECTORS.dropdownToggle).forEach(toggle => {
            toggle.setAttribute('aria-expanded', 'false');
        });
    }

    /**
     * Close the mobile menu
     */
    function closeMobileMenu() {
        const menuBtn = document.querySelector(SELECTORS.menuBtn);
        const navLinks = document.querySelector(SELECTORS.navLinks);

        if (!menuBtn || !navLinks) return;

        menuBtn.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('is-open');
        navLinks.setAttribute('aria-hidden', 'true');
        mobileMenuOpen = false;

        // Close all dropdowns when closing mobile menu
        closeAllDropdowns();
    }

    /**
     * Open the mobile menu
     */
    function openMobileMenu() {
        const menuBtn = document.querySelector(SELECTORS.menuBtn);
        const navLinks = document.querySelector(SELECTORS.navLinks);

        if (!menuBtn || !navLinks) return;

        menuBtn.setAttribute('aria-expanded', 'true');
        navLinks.classList.add('is-open');
        navLinks.setAttribute('aria-hidden', 'false');
        mobileMenuOpen = true;
    }

    /**
     * Toggle the mobile menu
     */
    function toggleMobileMenu() {
        if (mobileMenuOpen) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    }

    /**
     * Toggle a dropdown menu
     * @param {HTMLElement} toggle - The dropdown toggle button
     */
    function toggleDropdown(toggle) {
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

        // Close other dropdowns first (accordion behaviour)
        document.querySelectorAll(SELECTORS.dropdownToggle).forEach(otherToggle => {
            if (otherToggle !== toggle) {
                otherToggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Toggle this dropdown
        toggle.setAttribute('aria-expanded', !isExpanded);
    }

    // =============================================================================
    // Event Handlers
    // =============================================================================

    /**
     * Handle clicks on the mobile menu button
     */
    function handleMenuBtnClick(event) {
        event.preventDefault();
        toggleMobileMenu();
    }

    /**
     * Handle clicks on dropdown toggles
     */
    function handleDropdownToggleClick(event) {
        event.preventDefault();
        event.stopPropagation();
        toggleDropdown(event.currentTarget);
    }

    /**
     * Handle keyboard events for accessibility
     */
    function handleKeydown(event) {
        // Escape key closes any open menu/dropdown
        if (event.key === 'Escape') {
            closeAllDropdowns();

            // Also close mobile menu if open
            if (mobileMenuOpen) {
                closeMobileMenu();
                // Return focus to menu button
                const menuBtn = document.querySelector(SELECTORS.menuBtn);
                if (menuBtn) {
                    menuBtn.focus();
                }
            }
        }
    }

    /**
     * Handle clicks outside dropdowns to close them
     */
    function handleDocumentClick(event) {
        // Don't close if clicking inside a dropdown
        if (event.target.closest(SELECTORS.dropdown)) {
            return;
        }

        closeAllDropdowns();
    }

    /**
     * Handle window resize - close mobile menu on desktop breakpoint
     */
    function handleResize() {
        if (window.innerWidth >= 1024 && mobileMenuOpen) {
            closeMobileMenu();
        }
    }

    // =============================================================================
    // Initialization
    // =============================================================================

    function init() {
        // Mobile menu button
        const menuBtn = document.querySelector(SELECTORS.menuBtn);
        if (menuBtn) {
            menuBtn.addEventListener('click', handleMenuBtnClick);
        }

        // Dropdown toggles
        document.querySelectorAll(SELECTORS.dropdownToggle).forEach(toggle => {
            toggle.addEventListener('click', handleDropdownToggleClick);
        });

        // Keyboard navigation
        document.addEventListener('keydown', handleKeydown);

        // Click outside to close dropdowns
        document.addEventListener('click', handleDocumentClick);

        // Window resize handler
        window.addEventListener('resize', handleResize, { passive: true });

        // Initial state - set nav as hidden for screen readers on mobile
        const navLinks = document.querySelector(SELECTORS.navLinks);
        if (navLinks && window.innerWidth < 1024) {
            navLinks.setAttribute('aria-hidden', 'true');
        }
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
