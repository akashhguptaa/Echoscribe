import Navbar from '../components/Navbar'
import { useState } from 'react'
import Transcribe from '@/components/Transcribe'

export default function Home(){
   const [start, setStart] = useState<boolean>(false)
   const resetStart = ()=>{
    setStart(false)
   }
  return(
    <div className='bg-gradient-to-r from-[#E0F5F8] to-transparent '>

    {/* <Navbar resetStart={resetStart}/> */}
    <Transcribe />
    </div>
  )
}