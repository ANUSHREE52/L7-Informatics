document.addEventListener('DOMContentLoaded', function() {
    // Profile image preview
    const profileImageInput = document.getElementById('profileImage');
    const profileImagePreview = document.getElementById('profileImagePreview');
    
    if (profileImageInput && profileImagePreview) {
        profileImageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profileImagePreview.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Avatar management
    const avatarInput = document.getElementById('avatarInput');
    const uploadAvatarBtn = document.getElementById('uploadAvatarBtn');
    const avatarPreview = document.getElementById('avatarPreview');
    const removeAvatarBtn = document.getElementById('removeAvatarBtn');
    const saveAvatarBtn = document.getElementById('saveAvatarBtn');
    const defaultAvatars = document.getElementById('defaultAvatars');
    
    let selectedAvatar = null;
    
    if (uploadAvatarBtn && avatarInput) {
        uploadAvatarBtn.addEventListener('click', function() {
            avatarInput.click();
        });
        
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    avatarPreview.style.backgroundImage = `url('${e.target.result}')`;
                    selectedAvatar = e.target.result;
                    if (removeAvatarBtn) removeAvatarBtn.disabled = false;
                    
                    // Remove selection from default avatars
                    document.querySelectorAll('.avatar-option').forEach(el => {
                        el.classList.remove('selected');
                    });
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    if (defaultAvatars) {
        defaultAvatars.addEventListener('click', function(e) {
            const avatarOption = e.target.closest('.avatar-option');
            if (avatarOption) {
                // Update selected state
                document.querySelectorAll('.avatar-option').forEach(el => {
                    el.classList.remove('selected');
                });
                avatarOption.classList.add('selected');
                
                // Update preview
                const img = avatarOption.querySelector('img');
                if (img) {
                    selectedAvatar = img.src;
                    avatarPreview.style.backgroundImage = `url('${img.src}')`;
                    if (removeAvatarBtn) removeAvatarBtn.disabled = false;
                }
            }
        });
    }
    
    if (removeAvatarBtn) {
        removeAvatarBtn.addEventListener('click', function() {
            avatarPreview.style.backgroundImage = 'url(\'/static/images/default-avatar.png\')';
            selectedAvatar = null;
            this.disabled = true;
            
            // Remove selection from default avatars
            document.querySelectorAll('.avatar-option').forEach(el => {
                el.classList.remove('selected');
            });
        });
    }
    
    // Save avatar
    if (saveAvatarBtn) {
        saveAvatarBtn.addEventListener('click', function() {
            // Here you would typically send the selectedAvatar to the server
            // For now, we'll just close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('changeAvatarModal'));
            if (modal) modal.hide();
            
            // Show success message
            const toast = new bootstrap.Toast(document.getElementById('avatarUpdatedToast'));
            toast.show();
        });
    }
    
    // Delete account confirmation
    const confirmEmailInput = document.getElementById('confirmEmail');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    if (confirmEmailInput && confirmDeleteBtn) {
        confirmEmailInput.addEventListener('input', function() {
            confirmDeleteBtn.disabled = this.value.toLowerCase() !== '{{ user.email|lower }}';
        });
    }
    
    // Save preferences
    const savePrefsBtn = document.getElementById('savePreferences');
    if (savePrefsBtn) {
        savePrefsBtn.addEventListener('click', function() {
            // Here you would typically save the preferences to the server
            // For now, we'll just show a success message
            const toast = new bootstrap.Toast(document.getElementById('prefsSavedToast'));
            toast.show();
        });
    }
    
    // Handle all toggle switches
    const toggleSwitches = document.querySelectorAll('.form-check-input[type="checkbox"]');
    if (toggleSwitches.length > 0) {
        toggleSwitches.forEach(function(toggle) {
            toggle.addEventListener('change', function() {
                const settingName = this.id;
                const isEnabled = this.checked;
                
                // Here you would typically update the setting on the server
                console.log(`${settingName} is now ${isEnabled ? 'enabled' : 'disabled'}`);
                
                // Example of how you might send this to the server:
                // fetch('/update-setting/', {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json',
                //         'X-CSRFToken': '{{ csrf_token }}'
                //     },
                //     body: JSON.stringify({
                //         setting: settingName,
                //         value: isEnabled
                //     })
                // });
            });
        });
    }
});
