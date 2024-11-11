/*
* Defines a resizeImage function that reduces the image size to the maximum width and height specified by the maxWidth and maxHeight parameters.
*/

// Function to resize an image to the maximum width and height
export const resizeImage = (file: Blob, maxWidth: number, maxHeight: number): Promise<string> => {
  // Return a promise that resolves with the resized image
  return new Promise((resolve, reject) => {
    const img = new Image()
    const reader = new FileReader()

    // Read the file as a data URL
    reader.readAsDataURL(file)
    reader.onloadend = () => {
      // Set the image source to the data URL
      img.src = reader.result as string
      // Handle image loading
      img.onload = () => {

        // Create a canvas element
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')

        // Get the image dimensions
        let { width, height } = img

        // Calculate the new dimensions
        if (width > maxWidth || height > maxHeight) {
          // Calculate the aspect ratio
          if (width > height) {
            height = (maxWidth / width) * height
            width = maxWidth
          } else {
            width = (maxHeight / height) * width
            height = maxHeight
          }
        }

        // Set the canvas dimensions
        canvas.width = width
        canvas.height = height

        if (ctx) {
          ctx.drawImage(img, 0, 0, width, height)
        }

        // Convert the canvas to a base64 string
        const resizedBase64 = canvas.toDataURL('image/jpeg', 0.8)
        resolve(resizedBase64)
      }

      // Handle image loading errors
      img.onerror = error => {
        reject('Error loading image: ' + error)
      }
    }

    // Handle file reading errors
    reader.onerror = error => {
      reject('Error reading file: ' + error)
    }
  })
}
